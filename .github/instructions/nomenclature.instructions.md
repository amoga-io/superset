---
applyTo: "**"
---

# Nomenclature Guidelines

## Naming Guidelines

-   Use descriptive names that reveal intent, purpose, and usage
-   Names should explain why something exists and how it's used
-   Favor clarity over brevity
-   Maintain consistency within the codebase
-   Avoid abbreviations unless they're universally understood

## Naming Styles

-   Variables : Use nouns or noun phrases. Examples: `userData`, `firstName`, `paymentStatus`, `configOptions`
-   Functions & Methods : Use verbs or verb phrases that describe the action. Examples: `calculateTotal`, `getUserInfo`, `validateInput`, `sendNotification`
-   Boolean Variables : Prefix with is**, has**, can**, or should**. Examples: `isValid`, `hasPermission`, `canEdit`, `shouldRefresh`
-   Arrays : Use plural nouns. Examples: `users`, `productList`, `errorMessages`, `activeConnections`
-   Classes & Components : Use singular nouns or noun phrases. Examples: `RequestHandler`, `UserProfile`, `PaymentProcessor`, `DataValidator`
-   Constants : Use uppercase with meaningful names. Examples: `DEFAULT_TIMEOUT`, `API_BASE_URL`, `MAX_RETRY_COUNT`, `COLOR_PRIMARY`
-   Event Handlers : Use Prefix with handle or on. Examples: `handleSubmit`, `onUserLogin`, `handleInputChange`, `onPageLoad`
-   Interfaces & Types : Use Consider prefixing with I for interfaces (if preferred). Examples: `IUserData`, `IConfigOptions`, `AuthResponse`, `RequestParams`
-   Promises & Async Functions : Use Consider using future tense or suffixes like Async. Examples: `fetchUserData`, `getUserProfileAsync`, `loadConfigAsync`, `processPayment`
-   File & Folder Structure : Use lowercase with descriptive names. Group by feature or function type. Example: `auth/login_service.js`

## Casing Styles

-   camelCase : Used in Variables, function names, method names, property names. Examples: `userData`, `calculateTotal`, `firstName`, `isValidEmail`
-   PascalCase : Used in Class names, component names, type definitions. Examples: `UserProfile`, `DataService`, `AuthProvider`, `RequestHandler`
-   snake_case : Used in File names, folder names. Examples: `user_service`, `api_utils`, `auth_middleware`, `data_models`
-   UPPER_SNAKE_CASE : Used in Constants, environment variables. Examples: `MAX_RETRY_COUNT`, `API_KEY`, `DEFAULT_TIMEOUT`, `COLOR_PRIMARY`
-   kebab-case : Used in URLs, CSS class names, HTML IDs. Examples: `nav-container`, `user-profile`, `button-primary`, `form-wrapper`
