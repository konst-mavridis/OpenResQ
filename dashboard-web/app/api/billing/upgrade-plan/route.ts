import { NextResponse } from "next/server";
import Stripe from "stripe";
import { getAuth } from "firebase-admin/auth";
import { getFirestore } from "firebase-admin/firestore";
import { initializeApp, App } from "firebase-admin/app";
import { cert } from "firebase-admin/app";

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY as string);

// Initialize Firebase Admin (ensure you have FIREBASE_ADMIN_SDK_KEY in .env)
let firebaseApp: App | undefined;
try {
  const serviceAccount = JSON.parse(
    process.env.FIREBASE_ADMIN_SDK_KEY || "{}"
  );
  firebaseApp = initializeApp({
    credential: cert(serviceAccount),
  });
} catch (error) {
  console.error("Firebase Admin initialization failed:", error);
}

const db = firebaseApp ? getFirestore(firebaseApp) : null;
const auth = firebaseApp ? getAuth(firebaseApp) : null;

export async function POST(req: Request) {
  console.log("Upgrade Plan API Hit");
  try {
    const body = await req.json();
    const { planId, latitude, longitude, uid } = body;

    if (!uid) {
      return NextResponse.json(
        { error: "User ID required" },
        { status: 400 }
      );
    }

    // Verify user token
    const token = req.headers.get("authorization")?.replace("Bearer ", "");
    if (!token || !auth) {
      return NextResponse.json(
        { error: "Unauthorized" },
        { status: 401 }
      );
    }

    try {
      await auth.verifyIdToken(token);
    } catch (err) {
      return NextResponse.json(
        { error: "Invalid token" },
        { status: 401 }
      );
    }

    // Get user data from Firestore
    const userDoc = await db?.collection("users").doc(uid).get();
    const userData = userDoc?.data();

    if (!userData) {
      return NextResponse.json(
        { error: "User not found" },
        { status: 404 }
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
    if (!selectedPlan) {
      return NextResponse.json(
        { error: "Invalid plan ID" },
        { status: 400 }
      );
    }

    // Create Checkout Session for upgrade
    const lineItems: Stripe.Checkout.SessionCreateParams.LineItem[] = [
      {
        price: selectedPlan.price_id,
        quantity: 1,
      },
    ];

    // Add setup fee if upgrading from basic to pro or other tiers
    if (selectedPlan.setup_price_id) {
      lineItems.push({
        price: selectedPlan.setup_price_id,
        quantity: 1,
      });
    }

    const session = await stripe.checkout.sessions.create({
      customer_email: userData.email,
      payment_method_types: ["card"],
      line_items: lineItems,
      mode: "subscription",
      success_url: `${process.env.NEXT_PUBLIC_SITE_URL}/billing?upgrade=success&session_id={CHECKOUT_SESSION_ID}`,
      cancel_url: `${process.env.NEXT_PUBLIC_SITE_URL}/billing`,
      metadata: {
        planId,
        uid,
        orgName: userData.orgName || "Unknown",
        adminEmail: userData.email,
        upgradeType: "plan_upgrade",
      },
    });

    // Update user location in Firestore if provided
    if (latitude && longitude && db) {
      try {
        await db.collection("users").doc(uid).update({
          area: {
            latitude: parseFloat(latitude),
            longitude: parseFloat(longitude),
            radius_km: 20.0,
          },
          last_updated: new Date(),
        });
        console.log("User location updated for upgrade");
      } catch (locErr) {
        console.error("Failed to update location:", locErr);
        // Don't fail the entire request if location update fails
      }
    }

    // Record upgrade request in backend
    try {
      const backendUrl =
        process.env.BACKEND_API_URL || "https://openresq.onrender.com";
      const dbResponse = await fetch(
        `${backendUrl}/billing/public/record-upgrade`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            uid,
            planId,
            orgName: userData.orgName,
            adminEmail: userData.email,
            latitude,
            longitude,
          }),
        }
      );

      if (dbResponse.ok) {
        console.log("Upgrade recorded in backend successfully");
      } else {
        const errText = await dbResponse.text();
        console.error(`Backend returned ${dbResponse.status}: ${errText}`);
      }
    } catch (dbErr) {
      console.error("Failed to record upgrade in backend:", dbErr);
      // Continue - payment process should proceed
    }

    return NextResponse.json({ url: session.url });
  } catch (err) {
    console.error("Upgrade Plan Error:", err);
    return NextResponse.json(
      { error: err instanceof Error ? err.message : "Internal server error" },
      { status: 500 }
    );
  }
}
