# Mira Protocols

This document drafts the shared message envelope and the private-house
conversation model used by Mira and PyGDO connectors.

## Message envelope

The human-readable wire form is:

```text
#<channel> <username>:{<server>} <PAYLOAD>
##<irc-context> <username>:{<server>} <PAYLOAD>
###<house-room> <username>:{<server>} <PAYLOAD>
```

Examples:

```text
#wechall <gizmore>:{wc} hi mira
##irc_wechall <gizmore>:{7} a normal IRC message
###HQ2_LivingRoom <Marion>:{7} Hello Mira
```

Fields are deliberately simple:

- `#` is a general channel.
- `##` retains the existing IRC convention and identifies IRC context.
- `###` identifies a private house-system room.
- `<username>` is the displayed sender identity.
- `{server}` identifies the connector or server instance.
- `PAYLOAD` is the message body and must remain intact at the transport
  boundary.

The envelope is a routing and conversation format, not an authorization token.
A protocol-correct message may be answered normally, but sensitive, destructive,
privileged, or externally visible actions still require separate authorization.

## House-system rooms

### Purpose

A house system is a private, local collection of rooms for people, agents,
devices, and services sharing one physical or trusted digital environment. It
is a conversation space first: humans can ask questions, agents can report
state, and services can announce events without pretending that every message
is a command.

### Room naming

Use a stable slug after `###`, for example:

```text
###HQ2_LivingRoom
###HQ2_Workshop
###Mogwai_Dev
```

Room names should not contain credentials, personal secrets, or transient
session identifiers. Display names may be maintained separately from the
stable room slug.

### Participants

A participant can be a human, an AI, a connector, or a device. The sender
identity and server instance remain explicit so that a bridged message does
not silently become a different identity.

```text
###HQ2_LivingRoom <Marion>:{7} Is gizmore around?
###Mogwai_Dev <mira>:{local} file-change event received
```

Bridges must preserve the original envelope and add provenance rather than
rewriting the sender. A room may route an answer to another connector, but it
must not leak private-room content into a public channel by default.

## Mail bridge

Local Postfix mail can use plus-addressing to preserve the source account and
category:

```text
mira+wechall@localhost
mira+linkuup@localhost
mira+gwf3+errors@localhost
mira+wechall+spam@localhost
```

The complete extension after the first `+` is meaningful. A mail connector may
normalize it to a safe queue slug such as `gwf3-errors`, while retaining the
original envelope recipient in metadata. Mail must enter a private queue before
it becomes a PyGDO conversation; no automatic external reply is implied.

## Routing rules

1. Parse and validate the envelope before dispatch.
2. Preserve sender, server, room, and payload as received.
3. Treat `###` content as private unless an explicit bridge authorizes release.
4. Deduplicate bridged events with a stable event identifier.
5. Keep transport-independent method logic in PyGDO; connectors only adapt the
   envelope and delivery mechanism.
6. Log the minimum technical metadata needed for debugging. Do not log full
   private payloads by default.

## Draft event shape

Internal connectors may normalize an envelope to a structure like:

```json
{
  "scope": "house",
  "room": "HQ2_LivingRoom",
  "user": "Marion",
  "server": "7",
  "payload": "Hello Mira",
  "source": "tcp",
  "event_id": "connector-defined-stable-id"
}
```

The JSON shape is an internal adapter contract; the readable envelope remains
the interoperable human-facing form.
