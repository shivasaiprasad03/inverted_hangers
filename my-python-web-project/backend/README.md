# Backend Documentation

## Overview
This backend application is built using Python and Flask. It serves as the server-side component for the web project, handling requests from the frontend and providing the necessary data and functionality.

## Setup Instructions

1. **Clone the Repository**
   Clone this repository to your local machine using:
   ```
   git clone <repository-url>
   ```

2. **Navigate to the Backend Directory**
   Change your directory to the backend folder:
   ```
   cd my-python-web-project/backend
   ```

3. **Install Dependencies**
   It is recommended to use a virtual environment. You can create one using:
   ```
   python -m venv venv
   ```
   Activate the virtual environment:
   - On Windows:
     ```
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```
     source venv/bin/activate
     ```

   Then, install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. **Run the Application**
   Start the Flask server by running:
   ```
   python app.py
   ```
   The server will be accessible at `http://127.0.0.1:5000`.

## API Endpoints
- **POST /build_graph**: Accepts a list of URLs and builds a graph of learning resources.
- **POST /find_path**: Finds a learning path between two topics based on user input.
- **POST /update_learner**: Updates the learner's progress for a specific topic.

## Additional Information
Ensure that you have Python 3.x installed on your machine. For any issues or contributions, please refer to the main project README or contact the project maintainers.