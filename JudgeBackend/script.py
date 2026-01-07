from user.models import MyUser 
def create_users_from_file(file_path):
    """
    Reads a file with lines like 'username,password' and creates Django users.
    """
    created_users = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or "," not in line:
                continue  # skip empty or invalid lines
            username, password = line.split(",", 1)  # split only at the first comma
            username = username.strip()
            password = password.strip()
            
            # Check if user already exists
            if MyUser.objects.filter(username=username).exists():
                print(f"User '{username}' already exists, skipping.")
                continue
            
            # Create the user
            user = MyUser.objects.create_user(username=username, password=password)
            created_users.append(user)
            print(f"Created user: {username}")
    
    print(f"Total users created: {len(created_users)}")
    return created_users