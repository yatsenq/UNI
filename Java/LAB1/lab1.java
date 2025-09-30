import java.util.*;
import java.io.*;

public class IndividualTaskWithFile {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);

        while (true) {
            System.out.println("\n========== MAIN MENU ==========");
            System.out.println("1. Task 1: Minimal palindromes in matrix columns");
            System.out.println("2. Task 2: Processing a sequence of words");
            System.out.println("3. Task 3: Working with publications");
            System.out.println("0. Exit");
            System.out.print("Choose an option: ");

            int choice = scanner.nextInt();
            scanner.nextLine(); 

            switch (choice) {
                case 1:
                    Task1.run(scanner);
                    break;
                case 2:
                    Task2.run(scanner);
                    break;
                case 3:
                    Task3.run(scanner);
                    break;
                case 0:
                    System.out.println("exiting...");
                    return;
                default:
                    System.out.println("Invalid choice!");
            }
        }
    }
}

class Task1 {
    public static void run(Scanner scanner) {
        System.out.println("\n=== Task 1: Minimal palindromes in columns ===");

        System.out.print("Enter number of rows: ");
        int rows = scanner.nextInt();
        System.out.print("Enter number of columns: ");
        int cols = scanner.nextInt();

        int[][] matrix = new int[rows][cols];

        System.out.println("Enter matrix elements:");
        for (int i = 0; i < rows; i++) {
            for (int j = 0; j < cols; j++) {
                System.out.print("matrix[" + i + "][" + j + "] = ");
                matrix[i][j] = scanner.nextInt();
            }
        }

        System.out.println("\nMatrix:"); 
        for (int i = 0; i < rows; i++) {
            for (int j = 0; j < cols; j++) {
                System.out.printf("%6d ", matrix[i][j]);
            }
            System.out.println();
        }

        int[] result = new int[cols];
        for (int j = 0; j < cols; j++) {
            int minPalindrome = Integer.MAX_VALUE;
            boolean found = false;
            for (int i = 0; i < rows; i++) {
                if (isPalindrome(matrix[i][j])) {
                    minPalindrome = Math.min(minPalindrome, matrix[i][j]);
                    found = true;
                }
            }
            result[j] = found ? minPalindrome : -1; 
        }

        System.out.println("\nResulting vector (minimal palindromes per column):");
        for (int j = 0; j < cols; j++) {
            if (result[j] != -1) {
                System.out.println("Column " + j + ": " + result[j]);
            } else {
                System.out.println("Column " + j + ": no palindrome found");
            }
        }
    }

    private static boolean isPalindrome(int number) {
        String str = String.valueOf(Math.abs(number));
        if (str.length() < 2) return false; 
        int left = 0, right = str.length() - 1;
        while (left < right) {
            if (str.charAt(left) != str.charAt(right)) return false;
            left++;
            right--;
        }
        return true;
    }
}

class Task2 {
    public static void run(Scanner scanner) {
        System.out.println("\n=== Task 2: Processing a sequence of words ===");
        System.out.println("Enter a sequence of words, separated by commas:");
        String input = scanner.nextLine();

        String[] words = input.split(",");

        System.out.println("\nProcessed words:");
        for (String word : words) {
            word = word.trim();
            if (!word.isEmpty()) {
                System.out.println(word + " -> " + processWord(word));
            }
        }
    }

    private static String processWord(String word) {
        if (word.length() <= 1) return word;
        char lastChar = word.charAt(word.length() - 1);
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < word.length() - 1; i++) {
            if (word.charAt(i) != lastChar) sb.append(word.charAt(i));
        }
        sb.append(lastChar);
        return sb.toString();
    }
}

class Task3 {
    public static void run(Scanner scanner) {
        System.out.println("\n=== Task 3: Working with publications ===");

        Publication[] publications = null;

        System.out.println("Choose data input method:");
        System.out.println("1. Use built-in data (hardcoded)");
        System.out.println("2. Read data from file (publications.txt)");
        System.out.print("Your choice: ");
        int choice = scanner.nextInt();
        scanner.nextLine();

        if (choice == 1) {
            publications = getHardcodedData();
        } else if (choice == 2) {
            publications = readFromFile();
            if (publications == null) return;
        } else {
            System.out.println("Invalid choice!");
            return;
        }

        while (true) {
            System.out.println("\n--- Submenu ---");
            System.out.println("1. Show all publications");
            System.out.println("2. Sort by title");
            System.out.println("3. Find author with most books");
            System.out.println("4. Show magazines by genre");
            System.out.println("0. Return to main menu");
            System.out.print("Choose option: ");
            choice = scanner.nextInt();
            scanner.nextLine();

            switch (choice) {
                case 1: showAll(publications); break;
                case 2: sortByTitle(publications); break;
                case 3: findMostProductiveAuthor(publications); break;
                case 4: showMagazinesByGenre(publications, scanner); break;
                case 0: return;
                default: System.out.println("Invalid choice!"); break;
            }
        }
    }

    private static Publication[] getHardcodedData() {
        Publication[] publications = new Publication[8];
        publications[0] = new Book("Java Programming", 2023, "Tech Press", "John Smith", 450);
        publications[1] = new Magazine("Science Today", 2024, "Science Corp", 15, "Science");
        publications[2] = new Book("Data Structures", 2022, "Academic Press", "Jane Doe", 600);
        publications[3] = new Magazine("Fashion Weekly", 2024, "Style Media", 52, "Fashion");
        publications[4] = new Book("Algorithms", 2021, "Tech Press", "John Smith", 700);
        publications[5] = new Magazine("Tech Review", 2024, "IT World", 24, "Technology");
        publications[6] = new Book("Design Patterns", 2023, "Code Books", "John Smith", 380);
        publications[7] = new Magazine("Nature Explorer", 2024, "Nature Inc", 12, "Nature");
        return publications;
    }

    private static Publication[] readFromFile() {
        List<Publication> list = new ArrayList<>();
        try (BufferedReader br = new BufferedReader(new FileReader("LAB1/publications.txt"))) {
            String line;
            while ((line = br.readLine()) != null) {
                String[] parts = line.split(";");
                if (parts[0].equalsIgnoreCase("Book")) {
                    list.add(new Book(parts[1], Integer.parseInt(parts[2]), parts[3], parts[4], Integer.parseInt(parts[5])));
                } else if (parts[0].equalsIgnoreCase("Magazine")) {
                    list.add(new Magazine(parts[1], Integer.parseInt(parts[2]), parts[3], Integer.parseInt(parts[4]), parts[5]));
                }
            }
        } catch (IOException e) {
            System.out.println("Error reading file: " + e.getMessage());
            return null;
        }
        return list.toArray(new Publication[0]);
    }

    private static void showAll(Publication[] publications) {
        System.out.println("\nAll publications:");
        for (Publication pub : publications) System.out.println(pub);
    }

    private static void sortByTitle(Publication[] publications) {
        Publication[] sorted = publications.clone();
        Arrays.sort(sorted, Comparator.comparing(Publication::getTitle));
        System.out.println("\nPublications sorted by title:");
        for (Publication pub : sorted) System.out.println(pub);
    }

    private static void findMostProductiveAuthor(Publication[] publications) {
        Map<String, Integer> authorCount = new HashMap<>();
        for (Publication pub : publications) {
            if (pub instanceof Book) {
                Book book = (Book) pub;
                authorCount.put(book.getAuthor(), authorCount.getOrDefault(book.getAuthor(), 0) + 1);
            }
        }

        if (authorCount.isEmpty()) {
            System.out.println("No books found!");
            return;
        }

        String mostProductive = Collections.max(authorCount.entrySet(), Map.Entry.comparingByValue()).getKey();
        System.out.println("\nAuthor with most books: " + mostProductive);
        System.out.println("Books:");
        for (Publication pub : publications) {
            if (pub instanceof Book && ((Book) pub).getAuthor().equals(mostProductive)) {
                Book b = (Book) pub;
                System.out.println("- " + b.getTitle() + " (" + b.getPages() + " pages)");
            }
        }
    }

    private static void showMagazinesByGenre(Publication[] publications, Scanner scanner) {
        System.out.print("Enter magazine genre: ");
        String genre = scanner.nextLine();
        boolean found = false;
        System.out.println("\nMagazines in genre \"" + genre + "\":");
        for (Publication pub : publications) {
            if (pub instanceof Magazine) {
                Magazine mag = (Magazine) pub;
                if (mag.getGenre().equalsIgnoreCase(genre)) {
                    System.out.println(mag);
                    found = true;
                }
            }
        }
        if (!found) System.out.println("No magazines found in this genre!");
    }
}

abstract class Publication {
    protected String title;
    protected int year;
    protected String publisher;

    public Publication(String title, int year, String publisher) {
        this.title = title;
        this.year = year;
        this.publisher = publisher;
    }

    public String getTitle() { return title; }
    public abstract String getType();

    @Override
    public String toString() {
        return getType() + ": \"" + title + "\" (" + year + "), Publisher: " + publisher;
    }
}

class Book extends Publication {
    private String author;
    private int pages;

    public Book(String title, int year, String publisher, String author, int pages) {
        super(title, year, publisher);
        this.author = author;
        this.pages = pages;
    }

    public String getAuthor() { return author; }
    public int getPages() { return pages; }

    @Override
    public String getType() { return "Book"; }

    @Override
    public String toString() {
        return super.toString() + ", Author: " + author + ", Pages: " + pages;
    }
}

class Magazine extends Publication {
    private int number;
    private String genre;

    public Magazine(String title, int year, String publisher, int number, String genre) {
        super(title, year, publisher);
        this.number = number;
        this.genre = genre;
    }

    public int getNumber() { return number; }
    public String getGenre() { return genre; }

    @Override
    public String getType() { return "Magazine"; }

    @Override
    public String toString() {
        return super.toString() + ", Number: " + number + ", Genre: " + genre;
    }
}
