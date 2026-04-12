import { NextResponse } from "next/server";
import Stripe from "stripe";
import nodemailer from "nodemailer";

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY);

// Helper function to send welcome email
async function sendWelcomeEmail(email, name, orgName) {
  try {
    const SMTP_HOST = process.env.SMTP_HOST;
    const SMTP_PORT = parseInt(process.env.SMTP_PORT || "587");
    const SMTP_USER = process.env.SMTP_USER;
    const SMTP_PASS = process.env.SMTP_PASS;
    const SMTP_SECURE = process.env.SMTP_SECURE === "true";

    // Check if SMTP is configured
    if (!SMTP_HOST || !SMTP_USER || !SMTP_PASS) {
      console.warn("SMTP configuration incomplete. Email not sent.");
      return false;
    }

    const transporter = nodemailer.createTransport({
      host: SMTP_HOST,
      port: SMTP_PORT,
      secure: SMTP_SECURE,
      auth: {
        user: SMTP_USER,
        pass: SMTP_PASS,
      },
    });

    const htmlContent = `
    <html>
      <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
          <h1 style="color: #2563eb;">Welcome to OpenResQ</h1>
          
          <p>Hi <strong>${name}</strong>,</p>
          
          <p>Thank you for choosing OpenResQ! We are preparing your dedicated operational environment for <strong>${orgName}</strong>.</p>
          
          <p>You will receive an email shortly with instructions on how to access your dashboard.</p>
          
          <div style="background-color: #f0f4f8; padding: 15px; border-left: 4px solid #2563eb; margin: 20px 0;">
            <p><strong>What's next?</strong></p>
            <ul>
              <li>Check your email for dashboard access instructions</li>
              <li>Review the setup guide sent to your inbox</li>
              <li>Login to your dashboard at <a href="https://dashboard.openresq.org" style="color: #2563eb;">dashboard.openresq.org</a></li>
            </ul>
          </div>
          
          <p>If you have any questions or need assistance, please don't hesitate to <a href="https://openresq.org/contact" style="color: #2563eb;">contact us</a>.</p>
          
          <p>Best regards,<br><strong>The OpenResQ Team</strong></p>
          
          <hr style="margin-top: 30px; border: none; border-top: 1px solid #ddd;">
          <p style="font-size: 12px; color: #666;">
            OpenResQ - Emergency Response & Community Support<br>
            <a href="https://openresq.org" style="color: #2563eb;">openresq.org</a>
          </p>
        </div>
      </body>
    </html>
    `;

    const result = await transporter.sendMail({
      from: SMTP_USER,
      to: email,
      subject: "Welcome to OpenResQ - Setup Instructions",
      html: htmlContent,
      text: `Welcome to OpenResQ!\n\nHi ${name},\n\nThank you for choosing OpenResQ! We are preparing your dedicated operational environment for ${orgName}.\n\nYou will receive an email shortly with instructions on how to access your dashboard.\n\nWhat's next?\n- Check your email for dashboard access instructions\n- Review the setup guide sent to your inbox\n- Login to your dashboard at https://dashboard.openresq.org\n\nIf you have any questions, contact us at https://openresq.org/contact\n\nBest regards,\nThe OpenResQ Team`,
    });

    console.log("Welcome email sent:", result.messageId);
    return true;
  } catch (error) {
    console.error("Failed to send welcome email:", error);
    return false;
  }
}

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

    // Send welcome email with setup instructions
    const emailSent = await sendWelcomeEmail(email, name, orgName);
    if (!emailSent) {
      console.warn("Welcome email failed to send, but checkout session created");
    }

    return NextResponse.json({ url: session.url });
  } catch (err) {
    console.error("Stripe Error:", err);
    return NextResponse.json({ error: err.message }, { status: 500 });
  }
}
