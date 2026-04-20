import psycopg2
from psycopg2 import Error

# This is our class. Think of a class as a blueprint for creating objects that do specific tasks.
# In this case, the blueprint creates a tool specifically for talking to a PostgreSQL database.
class PostgreSQLManager:

    # The __init__ method is known as the "constructor". 
    # It runs automatically when you create a new instance of this class.
    # We use it to accept the database credentials (username, password, etc.).
    def __init__(self, host, database, user, password, port):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.port = port
        self.connection = None
        self.cursor = None

    # This method attempts to open the "tunnel" between Python and the Database.
    def connect(self):
        try:
            # We use the connect function from the psycopg2 library using the credentials stored above.
            self.connection = psycopg2.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password,
                port=self.port
            )
            
            # The 'cursor' is a control structure that enables traversal over the records in a database.
            # You can think of it as your pointer or finger that points at specific rows of data.
            self.cursor = self.connection.cursor()
            
            print("Successfully connected to the PostgreSQL database.")

        except Error as e:
            # If something goes wrong (like wrong password), we catch the error and print it.
            print(f"Error while connecting to PostgreSQL: {e}")

    # This method closes the connection to save resources.
    def disconnect(self):
        # Check if we actually have an open connection before trying to close it.
        if self.connection:
            self.cursor.close()
            self.connection.close()
            print("PostgreSQL connection is closed.")

    # ---------------------------------------------------------
    # SECTION 1: SETUP (Create a table to play with)
    # ---------------------------------------------------------

    def create_table(self):
        # We define a SQL query as a string. 
        # We are asking the database to create a table named 'employees' if it doesn't exist yet.
        query = """
        CREATE TABLE IF NOT EXISTS employees (
            id SERIAL PRIMARY KEY,  -- 'SERIAL' means auto-incrementing ID number
            name VARCHAR(100) NOT NULL, -- A text field for the name
            age INTEGER,
            department VARCHAR(100)
        );
        """
        self._execute_query(query)
        print("Table 'employees' checked/created successfully.")

    # ---------------------------------------------------------
    # SECTION 2: CREATE (C in CRUD) - Inserting Data
    # ---------------------------------------------------------

    def insert_employee(self, name, age, department):
        # This query uses placeholders '%s'. 
        # This is a security best practice to prevent SQL Injection attacks.
        # We never insert user input directly into the string.
        query = "INSERT INTO employees (name, age, department) VALUES (%s, %s, %s) RETURNING id;"
        
        # We pack the data into a tuple. Note the comma at the end!
        data = (name, age, department)
        
        # We call a helper method to run this.
        self._execute_query(query, data)
        print(f"Employee '{name}' added successfully.")

    # ---------------------------------------------------------
    # SECTION 3: READ (R in CRUD) - Fetching Data
    # ---------------------------------------------------------

    def get_all_employees(self):
        # The '*' means "all columns". So this grabs every row and every column from the table.
        query = "SELECT * FROM employees;"
        
        # We use a different helper method here because we expect data back (fetching).
        return self._fetch_data(query)

    def get_employee_by_id(self, employee_id):
        # This is a specific query. We only want the row where the ID matches.
        query = "SELECT * FROM employees WHERE id = %s;"
        data = (employee_id,)
        
        # fetchone() returns just the first matching record.
        results = self._fetch_data(query, data)
        if results:
            return results[0] # Return the actual row, not the list containing the row
        else:
            return None

    # ---------------------------------------------------------
    # SECTION 4: UPDATE (U in CRUD) - Modifying Data
    # ---------------------------------------------------------

    def update_employee_department(self, employee_id, new_department):
        # We are updating the 'department' column for the specific 'id'.
        query = "UPDATE employees SET department = %s WHERE id = %s;"
        data = (new_department, employee_id)
        
        self._execute_query(query, data)
        print(f"Employee ID {employee_id} moved to {new_department}.")

    def get_by_id_and_update(self, employee_id, new_age):
        """
        This is a slightly more complex transaction.
        1. We verify the employee exists (Get by ID).
        2. We update the record.
        """
        print(f"--- Starting Transaction for ID {employee_id} ---")
        
        try:
            # Step 1: Check if user exists
            query_get = "SELECT id FROM employees WHERE id = %s;"
            self.cursor.execute(query_get, (employee_id,))
            result = self.cursor.fetchone()

            if result:
                # Step 2: Update the user
                query_update = "UPDATE employees SET age = %s WHERE id = %s;"
                self.cursor.execute(query_update, (new_age, employee_id))
                
                # Commit is crucial here. Without it, the change won't be saved permanently.
                self.connection.commit() 
                print(f"Transaction successful: Age updated to {new_age}.")
            else:
                print("Transaction failed: Employee ID not found.")

        except Error as e:
            # If there is any error during the transaction, we must 'rollback'.
            # This ensures we don't save half-changes or corrupt the database.
            self.connection.rollback()
            print(f"Error during transaction: {e}. Changes rolled back.")

    # ---------------------------------------------------------
    # SECTION 5: DELETE (D in CRUD) - Removing Data
    # ---------------------------------------------------------

    def delete_employee(self, employee_id):
        query = "DELETE FROM employees WHERE id = %s;"
        data = (employee_id,)
        
        self._execute_query(query, data)
        print(f"Employee ID {employee_id} deleted successfully.")

    # ---------------------------------------------------------
    # SECTION 6: Complex / Custom Queries
    # ---------------------------------------------------------

    def get_complex_query(self, min_age):
        """
        Example of a more complex query.
        Fetch employees older than X, ordered by Name.
        """
        query = "SELECT * FROM employees WHERE age > %s ORDER BY name ASC;"
        data = (min_age,)
        
        return self._fetch_data(query, data)

    # ---------------------------------------------------------
    # HELPER METHODS (Internal Use)
    # ---------------------------------------------------------

    # This method is used for queries that change data (Insert, Update, Delete).
    # We put an underscore '_' in front to signify it is intended for internal use.
    def _execute_query(self, query, data=None):
        try:
            # We pass the query and the data separately. 
            # The library safely inserts the data into the placeholders.
            self.cursor.execute(query, data)
            
            # 'commit' saves the changes to the database permanently.
            # If you forget this, your changes disappear when the program ends!
            self.connection.commit()
            
        except Error as e:
            print(f"Error executing query: {e}")
            # If there is an error, we rollback to keep the database stable.
            self.connection.rollback()

    # This method is used for queries that only read data (Select).
    def _fetch_data(self, query, data=None):
        try:
            self.cursor.execute(query, data)
            
            # fetchall() grabs every row returned by the query as a list of tuples.
            result = self.cursor.fetchall()
            return result
            
        except Error as e:
            print(f"Error fetching data: {e}")
            return []


# ==========================================
# MAIN EXECUTION BLOCK
# ==========================================

if __name__ == "__main__":
    # 1. Configuration - Replace these with your actual database details
    db_config = {
        "host": "localhost",      # Usually localhost
        "database": "your_db_name", # Put your DB name here
        "user": "postgres",        # Put your user here
        "password": "your_password", # Put your password here
        "port": "5432"
    }

    # 2. Instantiate the class (Create the object)
    db_manager = PostgreSQLManager(**db_config)

    # 3. Connect to DB
    db_manager.connect()

    # 4. Create a table (Setup)
    db_manager.create_table()

    # 5. CREATE (Insert some dummy users)
    print("\n--- Inserting Data ---")
    db_manager.insert_employee("Alice Smith", 30, "HR")
    db_manager.insert_employee("Bob Jones", 45, "Engineering")
    db_manager.insert_employee("Charlie Day", 25, "Marketing")

    # 6. READ (Get all)
    print("\n--- Reading All Employees ---")
    employees = db_manager.get_all_employees()
    for emp in employees:
        print(emp)

    # 7. READ (Get by ID)
    print("\n--- Getting Employee by ID (1) ---")
    emp_one = db_manager.get_employee_by_id(1)
    print(f"Found: {emp_one}")

    # 8. UPDATE (Simple Update)
    print("\n--- Updating Department for ID 2 ---")
    db_manager.update_employee_department(2, "Management")

    # 9. COMPLEX (Get by ID and Update Logic)
    print("\n--- Get by ID and Update Workflow ---")
    db_manager.get_by_id_and_update(1, 31) # Update Alice's age to 31

    # 10. COMPLEX QUERY (Search)
    print("\n--- Complex Query: Age > 30 ---")
    seniors = db_manager.get_complex_query(30)
    for senior in seniors:
        print(senior)

    # 11. DELETE
    print("\n--- Deleting Employee ID 3 ---")
    db_manager.delete_employee(3)

    # Final read to see changes
    print("\n--- Final State of Table ---")
    print(db_manager.get_all_employees())

    # 12. Disconnect
    db_manager.disconnect()