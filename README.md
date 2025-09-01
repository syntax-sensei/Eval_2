# Digital Wallet API

## API Endpoints

- @app.get("/users/{user_id}") - Get user by user_id
- @app.post("/users/") - Create New users
- @app.put("/users/{user_id}") - Update user data
- @app.get("/wallet/{user_id}/balance") - Get Wallet Balance
- @app.post("/wallet/{user_id}/add-money") - Add Money to wallet
- @app.post("/wallet/{user_id}/withdraw") - Withdraw money from wallet
- @app.post("/transfer") - Initiate Peer-to-Peer transfer
- @app.get("/transfer/{transfer_id}") - Get Transfer Details

