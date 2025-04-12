# Mental Health Tracking System

A comprehensive web application for tracking and managing mental health, built with Flask and MongoDB. The system provides personalized mental health assessments, community support, and access to nearby medical facilities.

## 🌟 Features

- **Mental Health Assessment**
  - Personalized questions based on user profile
  - Track stress, anxiety, and anger levels
  - AI-powered response analysis using Google's Gemini
  - Visual dashboard with historical data

- **Community Support**
  - Join support groups
  - Community-based mental health tracking
  - Admin-managed group system

- **Nearby Medical Facilities**
  - Find mental health facilities near you
  - Real-time location-based search
  - Distance calculation and facility information
  - Interactive map interface

## 🛠️ Tech Stack

- **Backend**: Python Flask
- **Database**: MongoDB
- **AI/ML**: Google Gemini API
- **Location Services**: OpenCage Geocoding API
- **Frontend**: HTML, CSS, JavaScript
- **Styling**: TailwindCSS

## 📋 Prerequisites

- Python 3.8+
- MongoDB
- Node.js (for TailwindCSS)
- Git

## ⚙️ Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
# Flask Configuration
FLASK_SECRET_KEY=your_secret_key
FLASK_ENV=development
FLASK_DEBUG=True
FLASK_HOST=0.0.0.0

# MongoDB Configuration
MONGODB_USERNAME=your_mongodb_username
MONGODB_PASSWORD=your_mongodb_password
MONGODB_CLUSTER=your_cluster_name
MONGODB_DATABASE=your_database_name
MONGODB_URI=mongodb+srv://${MONGODB_USERNAME}:${MONGODB_PASSWORD}@${MONGODB_CLUSTER}.mongodb.net/${MONGODB_DATABASE}

# API Keys
GEMINI_API_KEY=your_gemini_api_key
OPENCAGE_API_KEY=your_opencage_api_key
```

## 🚀 Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd AISSMS
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your credentials
```

5. Run the application:
```bash
python app.py
```

## 📁 Project Structure 

AISSMS/
├── Backend/
│ ├── model/
│ │ ├── Admin.py
│ │ ├── States.py
│ │ └── User.py
│ ├── routes/
│ │ ├── Admin.py
│ │ └── User.py
│ └── utility/
│ ├── config.py
│ ├── gemini.py
│ └── map.py
├── static/
│ ├── styles/
│ │ ├── dashboard.css
│ │ ├── home.css
│ │ ├── navbar.css
│ │ └── notification.css
│ └── js/
├── templates/
│ ├── admin/
│ ├── layout/
│ ├── pages/
│ └── sign/
├── app.py
├── .env
└── requirements.txt

## 🔐 Security Features

- Password hashing using Werkzeug
- Secure session management
- Environment variable protection
- CSRF protection
- Secure API key handling

## 🌐 API Integrations

1. **Google Gemini AI**
   - Mental health assessment
   - Response analysis
   - Personalized question generation

2. **OpenCage Geocoding**
   - Location search
   - Coordinate conversion
   - Address validation

3. **OpenStreetMap**
   - Medical facility search
   - Distance calculation
   - Location mapping

## 👥 User Types

1. **Regular Users**
   - Track mental health
   - Join communities
   - Find nearby facilities
   - View personal dashboard

2. **Admin Users**
   - Create and manage groups
   - Monitor group activities
   - Manage community members

## 📊 Data Visualization

- Historical mental health trends
- Daily mood tracking
- Community engagement metrics
- Location-based facility mapping

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request


## 🙏 Acknowledgments

- Google Gemini API for AI capabilities
- OpenCage for geocoding services
- OpenStreetMap for location data
- MongoDB Atlas for database hosting

## 📞 Support

For support, email [nikhilkole.html@gmail.com] or join our community channel. 