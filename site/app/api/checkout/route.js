import { NextResponse } from "next/server";
import Stripe from "stripe";

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY);

export async function POST(req) {
  console.log("Checkout API Hit");
  try {
    const body = await req.json();
    const { planId, orgName, email, name } = body;

    const plans = {
      basic: {
        price_id: process.env.STRIPE_PRICE_BASIC, // Recurring
        setup_price_id: process.env.STRIPE_PRICE_BASIC_SETUP, // One-time
      },
      pro: {
        price_id: process.env.STRIPE_PRICE_PRO, // Recurring
        setup_price_id: process.env.STRIPE_PRICE_PRO_SETUP, // One-time
      },
    };

    const selectedPlan = plans[planId];
    if (!selectedPlan) {
      return NextResponse.json({ error: "Invalid plan ID" }, { status: 400 });
    }

    // Create a Checkout Session
    const session = await stripe.checkout.sessions.create({
      customer_email: email,
      payment_method_types: ["card"],
      line_items: [
        {
          price: selectedPlan.price_id,
          quantity: 1,
        },
        {
          price: selectedPlan.setup_price_id,
          quantity: 1,
        },
      ],
      mode: "subscription",
      success_url: `${process.env.NEXT_PUBLIC_SITE_URL}/checkout/success?session_id={CHECKOUT_SESSION_ID}`,
      cancel_url: `${process.env.NEXT_PUBLIC_SITE_URL}/pricing`,
      metadata: {
        planId,
        orgName,
        adminName: name,
        adminEmail: email,
      },
    });

    return NextResponse.json({ url: session.url });
  } catch (err) {
    console.error("Stripe Error:", err);
    return NextResponse.json({ error: err.message }, { status: 500 });
  }
}
