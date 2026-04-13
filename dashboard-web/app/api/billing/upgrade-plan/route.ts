"use server";

import { NextResponse } from "next/server";
import Stripe from "stripe";

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY as string);

export async function POST(req: Request) {
  console.log("Upgrade Plan API Hit");
  try {
    const body = await req.json();
    const { planId, latitude, longitude, email, uid } = body;

    console.log("Request body:", { planId, email, uid });

    if (!planId || !email || !uid) {
      return NextResponse.json(
        { error: "Plan ID, email, and uid required" },
        { status: 400 }
      );
    }

    const plans: Record<string, { price_id: string; setup_price_id?: string }> = {
      basic: {
        price_id: process.env.STRIPE_PRICE_BASIC || "",
        setup_price_id: process.env.STRIPE_PRICE_BASIC_SETUP,
      },
      pro: {
        price_id: process.env.STRIPE_PRICE_PRO || "",
        setup_price_id: process.env.STRIPE_PRICE_PRO_SETUP,
      },
    };

    const selectedPlan = plans[planId];
    if (!selectedPlan || !selectedPlan.price_id) {
      return NextResponse.json(
        { error: "Invalid plan ID or price not configured" },
        { status: 400 }
      );
    }

    // Find existing customer and subscription
    console.log("Looking for existing customer with email:", email);
    const customers = await stripe.customers.list({
      email: email,
      limit: 1,
    });

    let customerId: string | undefined;
    let existingSubscriptionId: string | undefined;

    if (customers.data.length > 0) {
      customerId = customers.data[0].id;
      console.log("Found existing customer:", customerId);

      // Get the customer's active subscription
      const subscriptions = await stripe.subscriptions.list({
        customer: customerId,
        status: "active",
        limit: 1,
      });

      if (subscriptions.data.length > 0) {
        existingSubscriptionId = subscriptions.data[0].id;
        console.log(`Found active subscription to cancel: ${existingSubscriptionId}`);
      } else {
        console.log("No active subscriptions found for customer");
      }
    } else {
      console.log("No existing customer found, will create new one");
    }

    // Create Checkout Session for upgrade
    const lineItems: Stripe.Checkout.SessionCreateParams.LineItem[] = [
      {
        price: selectedPlan.price_id,
        quantity: 1,
      },
    ];

    // Add setup fee if available
    if (selectedPlan.setup_price_id) {
      lineItems.push({
        price: selectedPlan.setup_price_id,
        quantity: 1,
      });
    }

    const session = await stripe.checkout.sessions.create({
      ...(customerId ? { customer: customerId } : { customer_email: email }),
      payment_method_types: ["card"],
      line_items: lineItems,
      mode: "subscription",
      success_url: `${process.env.NEXT_PUBLIC_SITE_URL}/billing?upgrade=success&session_id={CHECKOUT_SESSION_ID}`,
      cancel_url: `${process.env.NEXT_PUBLIC_SITE_URL}/billing`,
      metadata: {
        planId,
        uid,
        adminEmail: email,
        upgradeType: "plan_upgrade",
        latitude: latitude?.toString() || "",
        longitude: longitude?.toString() || "",
        existingSubscriptionId: existingSubscriptionId || "",
      },
    });

    console.log("Checkout session created:", {
      sessionId: session.id,
      customerId: customerId || "new",
      existingSubscriptionId,
      planId,
    });

    // Record upgrade request in backend
    try {
      const backendUrl =
        process.env.BACKEND_API_URL || "https://openresq.onrender.com";
      await fetch(`${backendUrl}/billing/public/record-upgrade`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          uid,
          plan_id: planId,
          admin_email: email,
          latitude,
          longitude,
        }),
      });
    } catch (dbErr) {
      console.error("Failed to record upgrade in backend:", dbErr);
      // Continue - payment process should proceed
    }

    return NextResponse.json({
      url: session.url,
      sessionId: session.id,
      existingSubscriptionId,
    });
  } catch (err) {
    console.error("Upgrade Plan Error:", err);
    return NextResponse.json(
      { error: err instanceof Error ? err.message : "Internal server error" },
      { status: 500 }
    );
  }
}

