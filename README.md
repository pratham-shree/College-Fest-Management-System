# College Fest Management System

A comprehensive web application for managing college festivals, events, and participants. Built with Flask backend and React frontend.

## Project Overview

Odyssey is a full-stack college fest management system that provides a platform for organizing and managing college festivals. The system supports multiple user roles including students, organizers, and administrators, with features for event management, registration, accommodation booking, and more.

## Architecture

The project follows a microservices architecture with:
- **Backend**: Flask REST API with PostgreSQL database
- **Frontend**: React.js with Mantine UI components
- **Authentication**: JWT-based authentication
- **Email Service**: Flask-Mail for notifications


## Features

### For Students
- User registration (Native/Guest students)
- Event browsing and registration
- Accommodation booking
- Profile management
- Real-time notifications

### For Organizers
- Event creation and management
- Resource allocation
- Winner declaration
- Profile management
- Authentication system

### For Administrators
- User management (Students & Organizers)
- Event oversight
- Accommodation management
- System notifications
- Administrative controls

## Technology Stack

### Backend
- **Framework**: Flask 3.0.2
- **Database**: PostgreSQL with psycopg2
- **Authentication**: Flask-JWT-Extended
- **Email**: Flask-Mail
- **Security**: bcrypt for password hashing
- **CORS**: Flask-CORS for cross-origin requests

### Frontend
- **Framework**: React 18.2.0
- **UI Library**: Mantine Core 7.6.0
- **Routing**: React Router DOM 6.22.1
- **Styling**: Tailwind CSS
- **Animations**: React Type Animation
- **Notifications**: Sonner
- **Icons**: Lucide React

## Prerequisites

- **Python**: 3.8 or higher
- **Node.js**: 16.0 or higher
- **PostgreSQL**: 12.0 or higher
- **npm**: 8.0 or higher

## Installation & Setup

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/pratham987/College-Fest-management-System.git
   cd "College fest management/dbms-backend-flask"
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Database Configuration**
   - Create a PostgreSQL database
   - Create a `database.ini` file with your database configuration:
   ```ini
   [postgresql]
   host=your_host
   database=your_database
   user=your_user
   password=your_password
   port=5432
   ```

5. **Environment Variables**
   Create a `.env` file with:
   ```env
   MAIL_USERNAME=your_email@example.com
   MAIL_PASSWORD=your_email_password
   JWT_SECRET_KEY=your_jwt_secret_key
   ```

6. **Run the Flask application**
   ```bash
   python app.py
   ```

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd "../dbms-frontend"
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Build Tailwind CSS**
   ```bash
   npm run build-css
   ```

4. **Start the development server**
   ```bash
   npm start
   ```

The application will be available at:
- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:5000`

## Database Schema

The system uses PostgreSQL with the following main tables:
- `STUDENT` - Student information and credentials
- `ORGANISERS` - Organizer details and permissions
- `EVENTS` - Event details and scheduling
- `REGISTRATIONS` - Event registrations
- `ACCOMMODATION` - Accommodation bookings
- `NOTIFICATIONS` - System notifications

## Authentication

The system uses JWT (JSON Web Tokens) for authentication:
- Tokens are issued upon successful login
- Role-based access control for different user types
- Secure password hashing using bcrypt

## Email Service

Integrated email notifications for:
- Password reset requests
- Event registrations
- Winner announcements
- System notifications

## Deployment

### Backend (Vercel)
The backend is configured for Vercel deployment with `vercel.json`

### Frontend
The React app can be deployed to any static hosting service:
```bash
npm run build
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## API Documentation

### Authentication Endpoints
- `POST /signup_student` - Student registration
- `POST /signup_organizer` - Organizer registration
- `POST /login` - User login
- `POST /forgot_password` - Password reset

### Event Endpoints
- `GET /events` - List all events
- `POST /events` - Create new event (Organizer only)
- `PUT /events/:id` - Update event (Organizer only)
- `DELETE /events/:id` - Delete event (Admin only)

### Registration Endpoints
- `POST /register` - Register for event
- `GET /registrations` - View user registrations

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Authors

- **Pratham** - [@pratham987](https://github.com/pratham987)

## Acknowledgments

- Flask and React communities for excellent documentation
- Mantine UI for beautiful components
- PostgreSQL for robust database support

## Support

For support, email pratham987@example.com or create an issue in the GitHub repository.

---

**Happy Coding!**
