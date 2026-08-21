+++
title = "How to Set Up Cloudflare for Your Website: DNS, Proxy and SSL Explained"
date = "2026-08-21T21:51:00+08:00"
draft = false
description = "A practical beginner-friendly guide to setting up Cloudflare for a website. Learn how to configure DNS records, understand Proxied vs DNS Only, choose the right SSL/TLS mode, avoid common setup mistakes, and troubleshoot Cloudflare errors such as 521, 522, 525, and 526."
featured = true
categories = ["Web & Hosting"]
tags = ["Cloudflare", "Cloudflare DNS", "Cloudflare setup", "Cloudflare proxy", "Cloudflare SSL", "Proxied vs DNS Only"]
+++

[Cloudflare](/tags/cloudflare/) is one of the first services I usually add when setting up a new website.

You can use it for DNS management, HTTPS, caching, CDN, basic security, and hiding your origin server behind Cloudflare's proxy.

The problem is that Cloudflare looks simple at first, but a few settings — especially **DNS records, the orange cloud, and SSL/TLS mode** — can easily cause confusion.

This guide explains the basic Cloudflare setup from start to finish, with a focus on the settings that actually matter for a normal website.

![How to Set Up Cloudflare for Your Website: DNS, Proxy and SSL Explained](/uploads/2026/08/a1f7e519-a8fe-429e-a9ac-20d2f2a32dbb-423f0e97.webp)

---

## What Does Cloudflare Actually Do?

Before changing any settings, it helps to understand where Cloudflare sits in your website setup.

A normal website might look like this:

```text
Visitor
   ↓
Domain
   ↓
Your Server
```

After enabling Cloudflare proxying:

```text
Visitor
   ↓
Cloudflare
   ↓
Your Server
```

Cloudflare becomes a layer between the visitor and your origin server.

For supported web traffic, this allows Cloudflare to provide features such as:

* DNS hosting
* CDN and caching
* HTTPS
* DDoS protection
* Web Application Firewall features
* Performance optimization
* Origin IP protection

You do not necessarily need to move your website or hosting to Cloudflare.

Your server can still be hosted on a VPS, shared hosting provider, dedicated server, or another cloud platform.

---

# Step 1: Add Your Domain to Cloudflare

Create a Cloudflare account and add your domain.

For example:

```text
example.com
```

Do not enter:

```text
https://example.com
```

or:

```text
www.example.com
```

Cloudflare will scan the domain and attempt to detect its existing DNS records.

This is an important step.

Before changing your domain's nameservers, compare the DNS records imported by Cloudflare with the records from your current DNS provider.

If an important record is missing, your website or [email](/tags/email/) may stop working after the nameserver change.

Cloudflare specifically recommends reviewing DNS records before activating the domain.

---

# Step 2: Change Your Nameservers

After adding your domain, Cloudflare normally assigns two nameservers.

They look similar to:

```text
alice.ns.cloudflare.com
bob.ns.cloudflare.com
```

The exact nameservers are different for each domain.

Now log in to the company where you registered your domain.

This could be:

* [Namecheap](/tags/namecheap/)
* Spaceship
* GoDaddy
* Porkbun
* another registrar

Find the **Nameserver** or **DNS Server** settings.

Replace the existing nameservers with the two nameservers provided by Cloudflare.

For a standard Cloudflare DNS setup, changing the domain's authoritative nameservers is what allows Cloudflare to manage DNS for the domain.

After the change, Cloudflare may take some time to detect the new configuration.

Once activated, DNS records should normally be managed from Cloudflare instead of your previous DNS provider.

---

# Step 3: Understand the Most Important DNS Records

For a basic website, you will usually encounter four important record types:

```text
A
AAAA
CNAME
MX
```

There are also TXT records, which are commonly used for verification, email security, and other services.

---

## A Record

An A record connects a hostname to an IPv4 address.

Example:

```text
Type: A
Name: @
Content: 203.0.113.10
```

The `@` usually represents the root domain:

```text
example.com
```

So this record means:

```text
example.com → 203.0.113.10
```

If your website runs directly on a VPS with a public IPv4 address, this is one of the most common configurations.

---

## AAAA Record

An AAAA record does the same thing as an A record, but for IPv6.

Example:

```text
Type: AAAA
Name: @
Content: 2001:db8::1
```

Do not create an AAAA record unless your server actually supports IPv6 correctly.

A broken IPv6 configuration can sometimes cause confusing connectivity problems.

---

## CNAME Record

A CNAME points one hostname to another hostname.

A common example is:

```text
Type: CNAME
Name: www
Target: example.com
```

This means:

```text
www.example.com → example.com
```

Instead of entering your server IP twice, `www` simply follows the main domain.

---

## MX Record

MX records control email delivery.

For example, if you use [Google](/tags/google/) [Workspace](/tags/workspace/) or another email provider, they will give you MX records that need to be added to DNS.

MX records should not be treated like website records.

They are not proxied through Cloudflare's normal HTTP proxy. Cloudflare's proxy applies to supported A, AAAA, and CNAME web records, while records such as MX and TXT remain DNS-only.

---

# Step 4: Understand the Orange Cloud

This is probably the most important Cloudflare concept for beginners.

Next to supported DNS records, Cloudflare shows a proxy status.

There are two common states:

```text
Proxied
DNS only
```

They are often referred to as:

```text
Orange cloud
Gray cloud
```

---

## Proxied — Orange Cloud

When proxying is enabled:

```text
Visitor
   ↓
Cloudflare
   ↓
Origin Server
```

Cloudflare handles the web request before forwarding it to your server.

This allows Cloudflare to provide its proxy-based security, caching and performance features.

It also prevents normal DNS queries from directly returning your origin server's IP address.

For normal website traffic, Cloudflare recommends proxying supported A, AAAA and CNAME records that serve HTTP or HTTPS.

A typical configuration might look like:

```text
A       @       203.0.113.10      Proxied
CNAME   www     example.com       Proxied
```

---

## DNS Only — Gray Cloud

When a record is set to DNS only:

```text
Visitor
   ↓
Origin Server
```

Cloudflare still answers DNS queries, but the web traffic does not pass through Cloudflare's HTTP proxy.

Your real server address may therefore be visible through DNS.

Cloudflare caching, proxy-based protection and HTTP traffic optimization will also not apply to that record.

DNS-only mode is commonly useful for services that should not pass through Cloudflare's HTTP proxy.

Examples can include:

* some mail-related hostnames
* domain verification records
* non-HTTP services
* third-party services that require direct DNS resolution

---

# Step 5: Configure SSL/TLS Correctly

After DNS, this is the setting most likely to cause problems.

Go to:

```text
SSL/TLS
→ Overview
```

Cloudflare provides different encryption modes.

The important ones for most self-hosted websites are:

```text
Full
Full (strict)
```

---

## Full

With Full mode, Cloudflare encrypts the connection between Cloudflare and your origin server, but it does not fully validate the origin certificate.

This means the origin may use a certificate that is self-signed or otherwise not publicly trusted.

Cloudflare currently recommends using Full or Full (strict) when possible rather than configurations that leave the origin connection unencrypted.

---

## Full (strict)

For most properly configured websites, **Full (strict)** should be the goal.

The connection looks like this:

```text
Visitor
   HTTPS
     ↓
Cloudflare
   HTTPS
     ↓
Origin Server
```

Cloudflare also validates the certificate presented by the origin server.

The origin certificate must be valid, unexpired and match the hostname.

Cloudflare describes Full (strict) as the preferred option when the origin server has a valid certificate.

---

# Which SSL Mode Should I Use?

For a modern website, a good target configuration is:

```text
Browser
   ↓ HTTPS
Cloudflare
   ↓ HTTPS
Origin Server
```

with:

```text
SSL/TLS Mode:
Full (strict)
```

If your origin does not yet have a valid certificate, fix the certificate configuration rather than permanently relying on a weaker setup.

You can use:

* Let's Encrypt
* another trusted certificate authority
* Cloudflare Origin CA

---

# A Simple Recommended DNS Setup

Imagine your website runs on a VPS with this IP:

```text
203.0.113.10
```

A basic Cloudflare configuration could look like this:

| Type  | Name | Target       | Proxy   |
| ----- | ---- | ------------ | ------- |
| A     | @    | 203.0.113.10 | Proxied |
| CNAME | www  | example.com  | Proxied |

This gives you:

```text
example.com
www.example.com
```

through Cloudflare.

If you also run an SSH hostname such as:

```text
ssh.example.com
```

you might instead use:

```text
A
ssh
203.0.113.10
DNS only
```

because normal SSH traffic is not regular HTTP/HTTPS website traffic.

---

# A Common Mistake: Proxying [Everything](/tags/everything/)

A beginner may see the orange cloud and assume:

> More orange clouds must be better.

That is not always true.

Cloudflare's normal proxy is primarily designed for supported web traffic.

Website records usually make sense as proxied:

```text
example.com
www.example.com
blog.example.com
app.example.com
```

But other services may need direct DNS resolution.

Examples include certain:

```text
mail
FTP
SSH
verification services
third-party platforms
```

So a useful rule is:

> Proxy web traffic. Do not blindly proxy every DNS record.

---

# Another Common Mistake: Exposing the Origin IP

Cloudflare can hide the server IP used by proxied DNS records, but only if you do not expose the same IP somewhere else.

For example, imagine:

```text
example.com → Proxied
```

but you also have:

```text
direct.example.com → DNS only → 203.0.113.10
```

Anyone can now resolve:

```text
direct.example.com
```

and discover:

```text
203.0.113.10
```

This partially defeats the purpose of hiding the origin behind Cloudflare.

The same problem can happen through:

* old DNS records
* mail servers
* unused subdomains
* server monitoring hostnames
* historical DNS databases

Cloudflare is useful, but it is not a substitute for properly securing the origin server itself.

---

# Common Cloudflare Errors

Once you understand the traffic path, many Cloudflare errors become easier to troubleshoot.

The request normally follows:

```text
Browser
→ Cloudflare
→ Origin Server
```

So when a website fails, ask:

```text
Can the browser reach Cloudflare?
Can Cloudflare reach the server?
Can the server handle the request?
Is HTTPS configured correctly?
```

---

## Error 521

This commonly indicates that Cloudflare cannot establish the expected connection to the origin web server.

Check:

* Is Nginx or Apache running?
* Is the server reachable?
* Is the firewall blocking Cloudflare?
* Is the correct IP configured in DNS?

---

## Error 522

This generally points to a timeout while Cloudflare is trying to reach the origin.

Check:

* server load
* firewall configuration
* network connectivity
* incorrect origin IP
* routing problems

---

## Error 525

This is related to the SSL handshake between Cloudflare and the origin server.

A common cause is that the origin HTTPS configuration is not working correctly.

Cloudflare notes that Full mode requires the origin to accept HTTPS connections on port 443 and present a certificate.

---

## Error 526

Error 526 is particularly associated with certificate validation when using Full (strict).

Check:

* Has the certificate expired?
* Does the certificate match the hostname?
* Is the full certificate chain installed?
* Is HTTPS working directly on the origin?

Cloudflare documents an invalid origin certificate as a reason visitors can receive a 526 error under Full (strict).

---

# My Recommended Basic Cloudflare Configuration

For a normal website hosted on a VPS, my starting configuration is usually:

```text
DNS
A @ → server IP → Proxied

DNS
CNAME www → example.com → Proxied

SSL/TLS
Full (strict)

HTTPS
Enabled
```

Then verify:

```text
https://example.com
https://www.example.com
```

Both should load correctly.

After the basic configuration works, you can gradually explore more Cloudflare features.

---

# Do You Need Every Cloudflare Feature?

No.

This is another common mistake.

Cloudflare has a large number of products and settings, but a small website does not need all of them.

For most websites, start with:

```text
DNS
Proxy
HTTPS
Basic caching
Basic security
```

Only add more advanced features when you actually have a reason to use them.

Complexity itself can become a source of problems.

---

# Final Thoughts

Cloudflare is easier to understand when you stop treating it as a collection of switches and instead think about where it sits in the network.

The basic architecture is:

```text
Domain
   ↓
Cloudflare DNS
   ↓
Cloudflare Proxy
   ↓
Your Origin Server
```

Once you understand that path, most settings become much easier to reason about.

For a typical self-hosted website, remember these four rules:

1. **Check your DNS records before changing nameservers.**
2. **Proxy normal HTTP/HTTPS website records.**
3. **Do not blindly proxy services that are not web traffic.**
4. **Use Full (strict) SSL/TLS when your origin certificate is configured correctly.**

Get these fundamentals right first.

Everything else in Cloudflare can be added later when you actually need it.
