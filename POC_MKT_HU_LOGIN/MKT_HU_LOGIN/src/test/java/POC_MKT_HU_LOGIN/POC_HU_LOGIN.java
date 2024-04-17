package POC_MKT_HU_LOGIN;

import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.By;
import org.openqa.selenium.Cookie;

public class POC_HU_LOGIN {

	public static void main(String[] args) throws InterruptedException {
		ChromeDriver driver = new ChromeDriver();
        driver.get("https://tvweb-hu-cdn.tv.yo-digital.com/");
        driver.manage().window().maximize();
        Thread.sleep(3000);
        driver.findElement(By.className("styles__LoginButton-ot1uy1-0")).click();
        driver.findElement(By.className("styles__CardStyled-ufbxwv-0")).click();
        driver.findElement(By.id("login-input")).sendKeys("mf4mt.iw11@freemail.hu");
        driver.findElement(By.id("login-default-button")).click();
        driver.findElement(By.id("password")).sendKeys("Mediafirst123456");
        driver.findElement(By.className("btn")).click();
        Cookie bffToken = driver.manage().getCookieNamed("bffToken"); // Change "bff-token" to the actual cookie name
        if (bffToken != null) {
            System.out.println("BFF Token: " + bffToken.getValue());
        } else {
            System.out.println("BFF Token not found in cookies");
        }

	}

}
