package movierental;

public class NewReleaseMovie extends Movie {

	public NewReleaseMovie(String title) {
		super(title, NEW_RELEASE);
	}
    
	public double getamount(Rental rental) {
    	return this.amount += rental.getDaysRented() *3;
    }
    
    public int getfrequentRentalPoint(Rental rental) {
    	if (rental.getDaysRented() > 1) {
    		return this.frequentRentalPoint += 2;
    	}
    	return this.frequentRentalPoint ++;
    }
}
