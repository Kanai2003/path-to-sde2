# REST Maturity

Think of REST Maturity like a video game leveling system for APIs. When a developer says an API is "RESTful," they usually mean it has reached a specific level of maturity.

The industry standard for measuring this is the Richardson Maturity Model. It breaks down the transition from a messy "web of chaos" to a perfect RESTful system into four levels (0 to 3).

## Level 0: The "Swamp of POX" (Plain Old XML)

At this level, you aren't really using the web; you’re just using it as a tunnel.

- **The Vibe** : Everything goes to one single URL (endpoint).

- **The Action** : You use only one HTTP method (usually POST).

- **Analogy** : Imagine a giant warehouse where you have to talk to one guy at the front desk for everything—ordering, returning, complaining, or checking stock. You just hand him different forms, and he handles it.

## Level 1: Resources

Now we start organizing. Instead of one endpoint, we create separate URLs for different things (resources).

- **The Vibe** : You have /books, /authors, and /users.

- **The Action**: You still probably use POST for everything, but at least you’re talking to the right department.

- **Analogy**: The warehouse now has different windows. Window A is for Books; Window B is for Authors. It’s organized, but you’re still handing the same generic "Action Form" to every window.

## Level 2: HTTP Verbs

This is where most professional APIs live today. We stop using POST for everything and start using the correct HTTP Methods (Verbs).

- **The Vibe**: We use the web the way it was designed.

- **The Action**: `GET` to read data. `POST` to create data. `PUT/PATCH` to update data. `DELETE` to remove data.

- **The Result**: You also use `HTTP Status Codes` (like 201 Created or 404 Not Found) to communicate what happened.

### The HTTP Status Code Cheat Sheet

Think of these like the universal hand signals for web servers. They are grouped by the first digit:

#### 2xx (Success): "Everything is cool."

- 200 OK: You asked for it, here it is.

- 201 Created: You posted something new, and it's officially saved.

- 204 No Content: I did what you asked, but I have nothing to show you (common for DELETE).

#### 3xx (Redirection): "Go over there instead."

- 301 Moved Permanently: This URL is dead; use this new one forever.

#### 4xx (Client Error): "You messed up."

- 400 Bad Request: Your data is garbled or missing something.

- 401 Unauthorized: I don't know who you are (login required).

- 403 Forbidden: I know who you are, but you aren't allowed in here.

- 404 Not Found: That URL doesn't exist.

#### 5xx (Server Error): "I messed up."

- 500 Internal Server Error: The server crashed or hit a bug.

- 503 Service Unavailable: I'm too busy or down for maintenance.

## Level 3: Hypermedia Controls (HATEOAS)

This is the "Final Boss" of REST. It stands for `Hypermedia As The Engine Of Application State`.

- **The Vibe**: The API tells you what you can do next.

- **The Action**: When you request a resource, the API response includes links to related actions.

- **Analogy**: You go to a restaurant and look at a menu. The menu doesn't just list food; it tells you, "If you want this burger, turn to page 5 to see the sides." You don't need to memorize the restaurant's layout; the menu guides you.
