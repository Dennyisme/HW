package movierental;

public class RegularMovie extends Movie {

	public RegularMovie(String title) {
		super(title, REGULAR);
	}
	
    public double getamount(Rental rental) {
    	this.amount += 2;
    	if (rental.getDaysRented()>2) {
            this.amount += (rental.getDaysRented() - 2) * 1.5;
    	}
    	return this.amount;
    }
    
    public int getfrequentRentalPoint(Rental rental) {
    	return this.frequentRentalPoint ++;
    }
}
