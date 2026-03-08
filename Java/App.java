public class App {

    public static void main(String[] args) {

        String user = "admin";
        String password = "123456"; // senha em texto claro (má prática)

        if(user.equals("admin") && password.equals("123456")){
            System.out.println("Login successful");
        } else {
            System.out.println("Invalid credentials");
        }

    }

}