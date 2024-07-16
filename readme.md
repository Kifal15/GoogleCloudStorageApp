# Google Cloud Storage App


**Link to app:** [https://modular-button-416311.de.r.appspot.com/](https://modular-button-416311.de.r.appspot.com/)  


## Introduction:
This project involves creating an Identity and Access Management service using Google Cloud Platform (GCP). The application includes functionalities such as user sign-up, sign-in, and storage management. It was developed using Flask and deployed on Google App Engine.

## Basic Functionalities:

1. **User Sign-Up:**
   - Allows new users to register by providing their credentials.
   - Each user is assigned a unique user ID.
   - Users are allocated 10 MB of storage space.

2. **User Sign-In:**
   - Enables registered users to log in by verifying their credentials.
   - Authenticated users can access their allocated storage space and associated functionalities.

3. **Storage Management:**
   - Users are provided with 10 MB of storage space.
   - The system tracks the "used_space" variable to monitor storage usage.
   - Users are prevented from uploading files that exceed their allocated storage limit.

4. **Alert System:**
   - Notifies users when their storage usage approaches the 10 MB limit.
   - Alerts users to manage their files when they are close to reaching their storage capacity.

5. **Data Isolation and Protection:**
   - Each user's data is isolated using unique user IDs.
   - Ensures secure storage and retrieval of user-specific data.

The project showcases the use of various GCP services to build a scalable and secure cloud-based application.
