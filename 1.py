def Factorial(n):
    if n == 0:
        return 1
    return n * Factorial(n-1)
    
if __name__ == "__main__":
    n = int(input("Enter n: "))
    print(f"The factorial of number {n} = {Factorial(n)}")