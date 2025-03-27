# AlgoClan task

## Objective
Design and implement a RESTful API using Django Rest Framework (DRF) that allows users to fetch and store weather data using the OpenWeather API.

---
## Stack
   - Django rest framework
   - MySQL
   - Redis

## Features
1. **User Authentication**:
   - JWT token-based authentication.
   - Users can register, log in, and obtain a token to access protected endpoints.

2. **Third-Party API Integration**:
   - Fetch weather data using the OpenWeather API.
   - Retrieve weather details based on lon and lat.

3. **REST API Endpoints**:
   - **User Authentication**:
     - `POST /api/auth/register/` → Register a new user.
     - `POST /api/auth/login/` → Obtain authentication token.
     - `POST /api/auth/logout/` → Logout and delete token.
     - `POST /api/auth/verify-email/` → email verification.

   - **Weather API**:
     - `GET /api/weather/?lon={longitude}&lat={latitude}` → Fetch weather details for a given lan & log (requires authentication).
     - `GET /api/weather/history/` → Retrieve previously searched weather records.

4. **Database Storage**:
   - Store fetched weather data with the following fields:
     - `user` (ForeignKey)
     - `longitude`
     - `latitude`
     - `temperature`
     - `description`
     - `timestamp`
   - Create a database in mysql and update it in .env file
   - Set up Redis server for caching and also update it in .env file
   
5. **Error Handling**:
   - Handled API errors (e.g., invalid lan &lon, rate limits, missing authentication).
   - Return proper HTTP status codes and JSON responses.

6. **Bonus Features (Optional)**:
   - Pagination for the `/api/weather/history/` endpoint .
   - Used Redis caching for faster responses.
   - Limit requests to 5 per minute per user to prevent excessive API calls (can be handled from env)

---

## Installation & Setup Instructions

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/nafeu-khan/algoclan
   cd algoclan
   ```

2. **Set Up a Virtual Environment**:
   ```bash
   python -m venv venv
   source venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Environment Variables**:
   - Create a `.env` file in the project root.
   - copy all from .env.example and paste it in .env then update from your end
     

5. **Apply Migrations**:
   ```bash
   python manage.py migrate
   ```

6. **Run the Server**:
   ```bash
   python manage.py runserver
   ```

---

## API Documentation

### User Authentication Endpoints
1. **Register a New User**:
   - **Endpoint**: `POST /api/register/`
   - **Request Body**:
     ```json
     {
       "username": "example",
       "password": "password123",
       "email":"a@g.ca"
     }
     ```
   - **Response**:
     ```json
        {
            "message": "User registration is completed successfully."
        }
     ```
     An verification link is sent to verify via email. Look at the console for now.
    1. **Email Verification**:
        - **Endpoint**: got from email. e.g. `POST /api/auth/verify-email/?uid=<link>&token=<id>`
        - **Response**:
          ```json
            {
                "message": "Email verified successfully."
            }
          ```

2. **Login**:
   - **Endpoint**: `POST /api/login/`
   - **Request Body**:
     ```json
     {
       "username": "example",
       "password": "password123"
     }
     ```
   - **Response**:
     ```json
        {
            "success": true,
            "message": "Login successful",
            "refresh": "<jwt token>",
            "access": "jwt token",
            "username": "algoclan2"
        }
     ```

3. **Logout**:
   - **Endpoint**: `POST /api/logout/`
   - **Headers**:
     ```
     Authorization: Bearer <jwt-token>
     ```
    - **Request Body**:
     ```json
        {
        "refresh_token": "<refresh token>"
        }
     ```
   - **Response**:
     ```json
        {
        "message": "Logged out successfully."
        }
     ```

### Weather API Endpoints
1. **Fetch Weather Details**:
   - **Endpoint**: `GET /api/weather/?lon={longitude}&lat={latitude}`
   - **Headers**:
     ```
     Authorization: Bearer <jwt-token>
     ```
   - **Response**:
     ```json
     {
       "longitude": 12.34,
       "latitude": 56.78,
       "temperature": 25.5,
       "description": "clear sky",
       "timestamp": "2023-01-01T12:00:00Z"
     }
     ```
     Here firstly check redis cache server, if yes,then sent response from cache else fetch api and store the response in cache server for future use.
     

2. **Retrieve Weather History**:
   - **Endpoint**: `GET /api/weather/history/`
   - **Headers**:
     ```
     Authorization: Bearer <jwt-token>
     ```
   - **Response**:
     ```json
     [
       {
         "longitude": 12.34,
         "latitude": 56.78,
         "temperature": 25.5,
         "description": "clear sky",
         "timestamp": "2023-01-01T12:00:00Z"
       },
       {"..."}
     ]
     ```

