import { NextResponse } from "next/server";
import Stripe from "stripe";

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY as string);

export async function GET(req: Request) {
  try {
    const { searchParams } = new URL(req.url);
    const sessionId = searchParams.get("session_id");

    console.log("Upgrade complete API called with sessionId:", sessionId);

    if (!sessionId) {
      return NextResponse.json(
        { error: "Session ID required" },
        { status: 400 }
      );
    }

    // Get the checkout session
    const session = await stripe.checkout.sessions.retrieve(sessionId, {
      expand: ["subscription"],
    });

    console.log("Session payment status:", session.payment_status);
    console.log("Session metadata:", session.metadata);

    if (session.payment_status !== "paid") {
      return NextResponse.json(
        { status: "unpaid", message: "Payment not completed" },
        { status: 200 }
      );
    }

    // Get the new subscription ID
    let newSubscriptionId: string | undefined;
    if (session.subscription) {
      newSubscriptionId = typeof session.subscription === "string" 
        ? session.subscription 
        : session.subscription.id;
    }

    const customerId = typeof session.customer === "string" ? session.customer : undefined;

    // Keep only the upgraded subscription by cancelling all prior customer subscriptions.
    if (customerId && newSubscriptionId) {
      try {
        const customerSubscriptions = await stripe.subscriptions.list({
          customer: customerId,
          status: "all",
          limit: 100,
        });

        const cancelCandidates = customerSubscriptions.data.filter(
          (sub) =>
            sub.id !== newSubscriptionId &&
            ["active", "trialing", "past_due", "unpaid", "incomplete"].includes(sub.status)
        );

        for (const oldSub of cancelCandidates) {
          try {
            console.log("Cancelling previous subscription:", oldSub.id, oldSub.status);
            await stripe.subscriptions.cancel(oldSub.id);
          } catch (cancelErr) {
            console.error(`Failed to cancel previous subscription ${oldSub.id}:`, cancelErr);
          }
        }

        console.log(
          `Subscription cleanup complete. Kept ${newSubscriptionId}, cancelled ${cancelCandidates.length} old subscription(s).`
        );
      } catch (listErr) {
        console.error("Failed to list/cancel previous subscriptions:", listErr);
      }
    }

    const resolvedPlanId =
      session.metadata?.planId ||
      session.metadata?.plan_id ||
      undefined;

    // Notify backend of successful upgrade
    try {
      const backendUrl =
        process.env.BACKEND_API_URL || "https://openresq.onrender.com";
      const backendPayload = {
        sessionId,
        adminEmail: session.customer_email,
        planId: resolvedPlanId,
        uid: session.metadata?.uid,
        subscriptionId: newSubscriptionId,
        customerId,
      };
      console.log("Notifying backend with:", backendPayload);
      
      const backendResponse = await fetch(
        `${backendUrl}/billing/public/upgrade-completed`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(backendPayload),
        }
      );
      
      const backendText = await backendResponse.text();
      console.log("Backend response status:", backendResponse.status);
      console.log("Backend response:", backendText);
      
      if (!backendResponse.ok) {
        console.warn(`⚠ Backend error: ${backendResponse.status} - ${backendText}`);
      } else {
        console.log("✓ Backend successfully updated plan");
      }
    } catch (dbErr) {
      console.error("Failed to notify backend of upgrade completion:", dbErr);
    }

    return NextResponse.json({
      status: "success",
      message: "Upgrade completed successfully",
      planId: resolvedPlanId,
      subscriptionId: newSubscriptionId,
    });
  } catch (err) {
    console.error("Upgrade completion error:", err);
    return NextResponse.json(
      { error: err instanceof Error ? err.message : "Internal server error" },
      { status: 500 }
    );
  }
}
