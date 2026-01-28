---
applyTo: "**"
---

# Technology Choices & Standards

Opinionated technology stack and implementation standards.

## Environment & Versions

### Runtime Versions

-   **Node.js:** 22 LTS (latest)
-   **npm:** 10.x (latest)
-   **PostgreSQL:** 17
-   **Redis:** 7.x (latest)

### Package Versions (Minimum)

No alternatives. No explanations for obvious choices. Just use these.

| Package                  | Version   | Use                    | Don't use            |
| ------------------------ | --------- | ---------------------- | -------------------- |
| react                    | ^19.2.3   | UI components          | -                    |
| vite                     | ^8.0.0    | Build tool, dev server | webpack, CRA         |
| tailwindcss              | ^4.1.18   | Styling                | styled-components    |
| @vitejs/plugin-react-swc | ^4.2.2    | JSX compilation        | @vitejs/plugin-react |
| react-router-dom         | ^7.11.0   | Routing                | -                    |
| @reduxjs/toolkit         | ^2.11.2   | State management       | zustand, jotai       |
| react-redux              | ^9.2.0    | Redux React bindings   | -                    |
| axios                    | ^1.13.2   | HTTP requests          | fetch                |
| date-fns                 | ^4.1.0    | Date formatting        | moment, dayjs        |
| @dnd-kit/core            | ^6.3.1    | Drag and drop          | react-beautiful-dnd  |
| motion                   | ^12.23.26 | Animations             | react-spring         |
| sonner                   | ^2.0.7    | Toast notifications    | react-toastify       |
| react-window             | ^2.2.3    | List virtualization    | react-virtualized    |
| nanoid                   | ^5.1.6    | ID generation          | uuid                 |
| express                  | ^5.2.1    | HTTP server            | fastify, koa         |
| prisma                   | ^7.2.0    | Database ORM           | sequelize, typeorm   |
| @prisma/client           | ^7.2.0    | Database queries       | -                    |
| zod                      | ^4.2.1    | Schema validation      | yup, joi             |
| jose                     | ^6.1.3    | JWT handling           | jsonwebtoken         |
| pino                     | ^10.1.0   | Logging                | winston              |

---

## Express 5.x Setup

```javascript
app.use(cors({ origin: process.env.FRONTEND_URL }));
app.use(compression());
app.use(express.json({ limit: "10mb" }));
app.use(rateLimit({ windowMs: 15 * 60 * 1000, max: 100 }));
```

-   Middleware order: body parsers, custom middleware, routes, error handlers
-   Use Express Router for modular routes
-   Centralized error handler as last middleware
-   Use middleware for auth

---

## API Response Format

```json
{
    "status": 1,
    "message": "Message sent successfully",
    "data": { "delivered": [{ "user@example.com": 2 }] }
}
```

**Error:**

```json
{
    "status": 0,
    "message": "Error description",
    "data": null
}
```

HTTP codes: `200`, `201` (created), `400`, `401` (not authenticated), `403` (not authorized), `404`, `500`
