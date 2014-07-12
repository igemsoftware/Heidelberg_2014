import org.igemathome.boinc.wrapper.BoincAPIWrapper;

public class MainTester {
	
	public static void main(String[] args){
		BoincAPIWrapper.init();
		System.out.println("Callied BoincAPIWrapper.init()");
		String s = System.console().readLine();
		System.out.println("Calling BoincAPIWrapper.finish(0)");
		BoincAPIWrapper.finish(0);
	}

}
