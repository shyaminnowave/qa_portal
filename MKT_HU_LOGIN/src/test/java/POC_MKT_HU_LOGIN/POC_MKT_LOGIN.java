package POC_MKT_HU_LOGIN;

import org.openqa.selenium.By;
import org.openqa.selenium.Cookie;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;

public class POC_MKT_LOGIN {

	public static void main(String[] args)throws InterruptedException {
		WebDriver driver = new ChromeDriver();
		driver.get("https://tvweb-mk-cdn.tv.yo-digital.com/");
		driver.manage().window().maximize();
		Thread.sleep(3000);
		driver.findElement(By.className("styles__LoginButton-ot1uy1-0")).click();
		driver.findElement(By.className("styles__CardStyled-ufbxwv-0")).click();
		driver.findElement(By.name("UserName")).sendKeys("Innowaveautodt@gmail.com");
		driver.findElement(By.name("Password")).sendKeys("!nnoDTproject2024");
		driver.findElement(By.id("btnLogin")).click();
		Cookie bffToken = driver.manage().getCookieNamed("bffToken"); // Change "bff-token" to the actual cookie name
		if (bffToken != null) {
			System.out.println("BFF Token: " + bffToken.getValue());
		} else {
			System.out.println("BFF Token not found in cookies");
		}

	}

}
