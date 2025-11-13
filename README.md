### Project: BuildForge - The Intelligent PC Builder's Workshop

**BuildForge** is a comprehensive web application designed for PC enthusiasts, from beginners to seasoned builders. It moves beyond a simple parts list by providing an intelligent, interactive workshop where users can design, validate, and share their dream PC builds. The platform integrates real-time compatibility checks, smart recommendations, and a community marketplace to create a one-stop hub for PC crafting.

---

### Core Features

#### 1. User Authentication & Profile Management
*   **Functionality:** Secure user registration, login, and session management. Users have a personal profile where they can manage their details and view their activity on the platform (builds, marketplace listings, reviews).
*   **Tables:** `User`, `Profile`.

#### 2. Dynamic Component Catalog
*   **Functionality:** A comprehensive and filterable catalog of PC components (CPUs, GPUs, Motherboards, RAM, Storage, PSUs, Cases). The catalog is populated and updated via a custom web scraping management command, ensuring a rich and realistic dataset without manual entry.
*   **Tables:** `Component`, `ComponentSpec`.

#### 3. Multi-Build Workshop
*   **Functionality:** The central workspace where users can create, name, and manage multiple PC build projects simultaneously. This allows for experimenting with different configurations (e.g., "Budget Gaming Rig," "4K Video Editing Station") and saving them all under one account.
*   **Tables:** `Build`, `BuildComponent` (linking table).

#### 4. Wishlist Management
*   **Functionality:** Allows users to save individual components they are interested in to a personal "Wishlist." This is perfect for tracking desired parts across different builds or for future upgrades.
*   **Tables:** `Wishlist` (linking `User` and `Component`).

#### 5. Component Review System
*   **Functionality:** A user-driven review system where community members can submit star ratings and detailed reviews for any component in the catalog, helping others make informed decisions.
*   **Tables:** `Review`.

---

### Unique & Intelligent Features

#### 6. Real-time Build Validation Engine
*   **Functionality:** As a user adds components to a build, the system provides instant, real-time feedback on critical compatibility and performance metrics. This engine includes:
    *   **Bottleneck Detector:** A rule-based system that analyzes the performance tiers of the selected CPU and GPU, issuing a clear warning if a significant performance mismatch (bottleneck) is detected.
    *   **PSU Calculator:** Automatically sums the power requirements (TDP) of the selected components, adds a safety margin, and displays a "Recommended PSU Wattage" to guide the user's power supply choice.
*   **Uniqueness:** This transforms the app from a passive list-maker into an active, intelligent assistant that prevents common build errors and optimizes performance.

#### 7. Smart Component Recommendation System
*   **Functionality:** This system actively helps users complete their builds. When a user has selected a core component (like a CPU), the recommendation engine will suggest compatible parts for other slots (like Motherboards or RAM). Recommendations are intelligently filtered based on:
    *   **Compatibility:** Only shows parts that are physically compatible (e.g., LGA 1700 motherboards for a 13th Gen Intel CPU).
    *   **Performance Tiers:** Suggests components in a similar performance tier to avoid bottlenecks.
    *   **Budget:** Prioritizes components that fit within a user-defined target budget for the build.
*   **Uniqueness:** This feature demonstrates complex relational queries and business logic, providing a guided and user-friendly experience that dramatically simplifies the build process.

#### 8. Curated Pre-Built Guides & "One-Click" Cloning
*   **Functionality:** For beginners, BuildForge offers a selection of curated, pre-configured PC builds created by administrators (or expert users). These "guides" are optimized for specific use-cases and price points (e.g., "The $800 Esports Starter," "The $2000 Content Creator Pro").
*   Any user can view these guides and, with a single click, **clone the entire parts list** into their own Multi-Build Workshop to use as a starting point for their own customizations.
*   **Uniqueness:** This feature serves a different user segment (beginners), adds value through expert curation, and showcases a practical "template" or "clone" database operation.

#### 9. Collaborative Build Sharing
*   **Functionality:** Every build in a user's workshop has a unique, shareable URL. Anyone with the link can view the complete parts list, including the validation engine's feedback. A logged-in user visiting the link will see a "Copy to My Workshop" button, allowing them to instantly import and modify the shared build.
*   **Uniqueness:** This fosters collaboration and community interaction, turning a personal tool into a social one. It's a powerful demonstration of sharing and replicating complex relational data between users.

#### 10. Community Marketplace for Secondhand Parts
*   **Functionality:** This feature addresses the teacher's "transaction" requirement in a unique way. It's a dedicated classifieds section where users can create listings to buy and sell their used PC components.
*   Listings include photos, descriptions, asking price, and a link to the seller's BuildForge profile. The platform facilitates the connection, while the transaction itself happens offline.
*   **Uniqueness:** This creates a self-sustaining community ecosystem within the app and fulfills the project requirements without the immense complexity of a full e-commerce payment and shipping system.
