Simple chat product, which enables users to chat and report users if
necessary, and managers can ban/unban users.  Kind of an IRC light.

Anyone with a View permission can participate in the chat and report
users, while users with the Manage permission can ban/unban.

Uses the CreateAppendGet product to store and retrieve chat content,
so that a growing PersistentList or PersistentDict doesn't bloat the
database too much.  Maybe CAG is wholly unecessary but it seemed like
a good idea at the time.

Suitable for example in a pop-up window, as the format and style of
the product is very simple.

Works with and without Javascript enabled in the users' browser, and
made specificially to be accessible for users with visual impairments.
Ajax fetching and sending of chat lines is disabled for Internet
Explorer.

Created initially for the The Norwegian Association of the Blind and
Partially Sighted - NABP (blindeforbundet.no/internett/english-info).

Available in English and Norwegian.
