# 📝 Todo API

This project is a simple Todo API built with FastAPI and SQLAlchemy. It provides basic CRUD operations for managing todo items.

## 🌟 Features

- Create a new todo item
- Retrieve a specific todo item by id
- Update a specific todo item by id
- Delete a specific todo item by id

## 🚀 Endpoints

- `POST /api/todo/create`: Create a new todo item
- `GET /api/todo/{todo_id}`: Retrieve a specific todo item by id
- `PUT /api/todo/update/{todo_id}`: Update a specific todo item by id
- `DELETE /api/todo/delete/{todo_id}`: Delete a specific todo item by id

## 🛠️ Installation

Clone the repository:

```bash
git clone https://github.com/aaxyat/todo-api.git
cd todo-api
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

## 🏃‍♂️ Usage

Start the server:

```bash
uvicorn app:app --reload
```

Now you can visit `http://localhost:8000` to view the application.

## 🧪 How to Run Tests

To run the tests:

```bash
pytest
```

## 🤝 Contributing

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

[MIT](LICENSE)
