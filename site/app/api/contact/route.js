import fs from 'fs';
import path from 'path';
import nodemailer from 'nodemailer';

export async function POST(req) {
  try {
    const { name, email, subject, message } = await req.json();

    if (!name || !email || !subject || !message) {
      return new Response(JSON.stringify({ error: 'Required fields are missing.' }), { status: 400 });
    }

    // Normalize env names (support both variants)
    const SMTP_HOST = process.env.SMTP_HOST;
    const SMTP_PORT = process.env.SMTP_PORT || '587';
    const SMTP_USER = process.env.SMTP_USER || process.env.EMAIL_USER;
    const SMTP_PASS = process.env.SMTP_PASS || process.env.EMAIL_PASS;
    const SMTP_SECURE = (process.env.SMTP_SECURE || 'false') === 'true';
    const CONTACT_RECIPIENT = process.env.CONTACT_RECIPIENT || process.env.TO_EMAIL;
    const BACKEND_URL = process.env.CONTACT_BACKEND_URL || 'http://localhost:5000/api/contact';

    const canUseSmtp = SMTP_USER && SMTP_PASS && CONTACT_RECIPIENT;

    // If SMTP unavailable, try forwarding to an external backend
    if (!canUseSmtp) {
      try {
        const forwardRes = await fetch(BACKEND_URL, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ name, email, subject, message }),
        });

        const forwardData = await forwardRes.json().catch(() => ({}));

        if (!forwardRes.ok) {
          throw new Error(forwardData.error || forwardData.message || `Forward failed with status ${forwardRes.status}`);
        }

        return new Response(JSON.stringify({ message: forwardData.message || 'Message forwarded to backend' }), { status: 200 });
      } catch (err) {
        console.error('Forwarding failed:', err);
        // continue to fallback to file storage
      }
    }

    // Prepare transporter (SMTP or gmail service)
    let transporter;
    if (SMTP_HOST) {
      transporter = nodemailer.createTransport({
        host: SMTP_HOST,
        port: Number(SMTP_PORT),
        secure: SMTP_SECURE,
        auth: { user: SMTP_USER, pass: SMTP_PASS },
      });
    } else {
      transporter = nodemailer.createTransport({
        service: 'gmail',
        auth: { user: SMTP_USER, pass: SMTP_PASS },
      });
    }

    const mailBody = `New contact form submission from OpenResQ\n\nName: ${name}\nEmail: ${email}\nSubject: ${subject}\n\nMessage:\n${message}\n\nReceived: ${new Date().toISOString()}`;

    try {
      await transporter.sendMail({
        from: `"OpenResQ Contact" <${SMTP_USER}>`,
        to: CONTACT_RECIPIENT,
        subject: `OpenResQ contact from ${name}`,
        text: mailBody,
        html: mailBody.replace(/\n/g, '<br/>'),
        replyTo: email,
      });

      // Auto-reply (best-effort)
      const autoReplyBody = `${name ? `Dear ${name},` : 'Hello,'}\n\nThank you for contacting OpenResQ. We have received your message and a member of our team will review it shortly. If your request is urgent, please include a phone number or call local emergency services if appropriate.\n\nWhat to expect:\n- We will reply within 1-2 business days.\n- If additional information is needed, we may follow up by email.\n\nBest regards,\nOpenResQ Team`;

      try {
        await transporter.sendMail({
          from: `"OpenResQ" <${SMTP_USER}>`,
          to: email,
          subject: 'We received your message — OpenResQ',
          text: autoReplyBody,
          html: autoReplyBody.replace(/\n/g, '<br/>'),
        });
      } catch (autoErr) {
        console.error('Auto-reply failed:', autoErr);
      }

      return new Response(JSON.stringify({ message: 'Message sent successfully' }), { status: 200 });
    } catch (mailErr) {
      console.error('Mail send failed:', mailErr);

      // Fallback: persist to a local file
      const filePath = path.join(process.cwd(), 'contacts.json');
      let contacts = [];
      if (fs.existsSync(filePath)) {
        try { contacts = JSON.parse(fs.readFileSync(filePath, 'utf-8')); } catch (e) { contacts = []; }
      }
      contacts.push({ name, email, subject, message, createdAt: new Date().toISOString(), error: String(mailErr) });
      fs.writeFileSync(filePath, JSON.stringify(contacts, null, 2));

      return new Response(JSON.stringify({ error: 'Failed to send email; message saved locally.' }), { status: 500 });
    }
  } catch (error) {
    console.error(error);
    return new Response(JSON.stringify({ error: 'Something went wrong' }), { status: 500 });
  }
}