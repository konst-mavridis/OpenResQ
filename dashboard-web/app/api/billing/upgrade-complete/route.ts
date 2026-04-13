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

    const existingSubId = session.metadata?.existingSubscriptionId;
    console.log("Existing subscription ID from metadata:", existingSubId);

    // Cancel the old subscription if it exists
    if (existingSubId && existingSubId !== "") {
      try {
        console.log("Attempting to cancel subscription:", existingSubId);
        await stripe.subscriptions.cancel(existingSubId);
        console.log(`✓ Successfully cancelled old subscription: ${existingSubId}`);
      } catch (cancelErr) {
        console.error(`✗ Failed to cancel subscription ${existingSubId}:`, cancelErr);
        // Don't fail the upgrade if cancellation fails
      }
    } else {
      console.log("No existing subscription to cancel");
    }

    // Get the new subscription ID
    let newSubscriptionId: string | undefined;
    if (session.subscription) {
      newSubscriptionId = typeof session.subscription === "string" 
        ? session.subscription 
        : session.subscription.id;
    }

    // Notify backend of successful upgrade
    try {
      const backendUrl =
        process.env.BACKEND_API_URL || "https://openresq.onrender.com";
      const backendPayload = {
        sessionId,
        adminEmail: session.customer_email,
        planId: session.metadata?.planId,
        uid: session.metadata?.uid,
        subscriptionId: newSubscriptionId,
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
      
      console.log("Backend response status:", backendResponse.status);
    } catch (dbErr) {
      console.error("Failed to notify backend of upgrade completion:", dbErr);
    }

    return NextResponse.json({
      status: "success",
      message: "Upgrade completed successfully",
      planId: session.metadata?.planId,
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
