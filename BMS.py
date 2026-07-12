class BankAccount:
    def __init__(self, account_number, account_holder):
        self.account_number = account_number
        self.account_holder = account_holder
        self.balance = 0

    def deposit(self, amount):
        if amount > 0:
            self.balance += amount
            print(f"Deposited: {amount}. New Balance: {self.balance}")
        else:
            print("Deposit amount must be positive.")

    def withdraw(self, amount):
        if 0 < amount <= self.balance:
            self.balance -= amount
            print(f"Withdrew: {amount}. New Balance: {self.balance}")
        else:
            print("Invalid withdrawal amount.")

    def check_balance(self):
        print(f"Current Balance: {self.balance}")

def main():
    accounts = {}
    while True:
        print("\n1. Create Account\n2. Deposit\n3. Withdraw\n4. Check Balance\n5. Exit")
        choice = input("Choose an option: ")
        
        if choice == '1':
            acc_num = input("Enter account number: ")
            holder = input("Enter account holder name: ")
            accounts[acc_num] = BankAccount(acc_num, holder)
            print("Account created successfully.")
        
        elif choice == '2':
            acc_num = input("Enter account number: ")
            amount = float(input("Enter amount to deposit: "))
            if acc_num in accounts:
                accounts[acc_num].deposit(amount)
            else:
                print("Account not found.")
        
        elif choice == '3':
            acc_num = input("Enter account number: ")
            amount = float(input("Enter amount to withdraw: "))
            if acc_num in accounts:
                accounts[acc_num].withdraw(amount)
            else:
                print("Account not found.")
        
        elif choice == '4':
            acc_num = input("Enter account number: ")
            if acc_num in accounts:
                accounts[acc_num].check_balance()
            else:
                print("Account not found.")
        
        elif choice == '5':
            print("Exiting...")
            break
        
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()