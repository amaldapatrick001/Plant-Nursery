package Definition;

import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.firefox.FirefoxDriver;
import io.cucumber.java.en.And;
import io.cucumber.java.en.Given;
import io.cucumber.java.en.Then;
import io.cucumber.java.en.When;

public class StepDefinitions {
    private WebDriver driver = null;

    @Given("browser is open")
    public void browser_is_open() {
        System.out.println("Inside step-Browser is open");
        System.setProperty("webdriver.gecko.driver", "C:\\Users\\hp\\eclipse-workspace\\eden1\\src\\test\\resources\\drivers\\geckodriver.exe");
        driver = new FirefoxDriver();
        driver.manage().window().maximize();
    }

    @And("user is on login page")
    public void user_is_on_login_page() throws Exception {
        driver.navigate().to("http://127.0.0.1:8000/userauths/login/");
    }

    @When("user enters username and password")
    public void user_enters_username_and_password() throws Throwable {
        driver.findElement(By.id("id_email")).sendKeys("augustopatrickputhenpurayil@gmail.com");
        driver.findElement(By.id("id_password")).sendKeys("Augo@123");
    }

    @Then("user clicks on login")
    public void user_clicks_on_login() {
        driver.findElement(By.id("login")).click();
    }

    @Then("user navigates to disease detection page")
    public void user_navigates_to_disease_detection_page() throws InterruptedException {
        Thread.sleep(2000); // Wait for page to load
        driver.findElement(By.linkText("Disease Detection")).click();
    }

    @When("user uploads a plant image")
    public void user_uploads_a_plant_image() {
        String imagePath = "C:\\Users\\hp\\Downloads\\download (47).jpg";
        driver.findElement(By.id("image")).sendKeys(imagePath);
    }

    @And("clicks on detect disease button")
    public void clicks_on_detect_disease_button() {
        driver.findElement(By.xpath("//button[contains(text(),'Detect Disease')]")).click();
    }
} 