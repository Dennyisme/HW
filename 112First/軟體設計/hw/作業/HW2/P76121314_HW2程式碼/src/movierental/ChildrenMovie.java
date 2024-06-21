package movierental;

public class ChildrenMovie extends Movie {

	public ChildrenMovie(String title) {
		super(title, CHILDRENS);
	}
	
    public double getamount(Rental rental) {
    	this.amount += 1.5;
    	if(rental.getDaysRented() > 3) {
    		this.amount += (rental.getDaysRented() - 2) * 1.5;
    	}
    	return this.amount;
    }
    
    public int getfrequentRentalPoint(Rental rental) {
    	return this.frequentRentalPoint ++;
    }


}
