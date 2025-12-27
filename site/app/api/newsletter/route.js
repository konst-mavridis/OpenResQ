import fs from "fs";
import path from "path";

export async function POST(req) {
  try {
    const { email } = await req.json();

    if (!email || !email.includes("@")) {
      return new Response(JSON.stringify({ error: "Invalid email" }), {
        status: 400,
      });
    }

    // Αρχείο για αποθήκευση emails
    const filePath = path.join(process.cwd(), "emails.json");

    let emails = [];
    if (fs.existsSync(filePath)) {
      const data = fs.readFileSync(filePath, "utf-8");
      emails = JSON.parse(data);
    }

    if (emails.includes(email)) {
      return new Response(JSON.stringify({ message: "Email already subscribed" }), {
        status: 200,
      });
    }

    emails.push(email);
    fs.writeFileSync(filePath, JSON.stringify(emails, null, 2));

    return new Response(JSON.stringify({ message: "Subscribed successfully" }), {
      status: 200,
    });
  } catch (error) {
    console.error(error);
    return new Response(JSON.stringify({ error: "Something went wrong" }), {
      status: 500,
    });
  }
}
