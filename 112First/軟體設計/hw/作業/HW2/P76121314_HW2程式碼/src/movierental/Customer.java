package movierental;

import java.util.ArrayList;
import java.util.List;

public class Customer {

    private String _name;
    private List<Rental> _rentals = new ArrayList<Rental>();

    public Customer(String name) {
        _name = name;
    }

    public void addRental(Rental arg) {
        _rentals.add(arg);
    }

    public String getName() {
        return _name;
    }

    public String statement() {
    	
        String result = "<h1>Rental Record for <em>" + getName() + "</em></h1>\n";
        result += "<table>\n";
        double totalAmount = 0;
		int frequentRenterPoints = 0;
		for (Rental each : this._rentals) {
			frequentRenterPoints += each.getMovie().getfrequentRentalPoint(each);
			double thisamount = each.getMovie().getamount(each);
	        totalAmount += thisamount;

	        // show figures for this rental
			result +="  <tr><td>" + each.getMovie().getTitle() + "</td><td>" + String.valueOf(thisamount) + "</td></tr>\n";
		} 
		result += "</table>\n";
		result += "<p>Amount owed is <em>" + String.valueOf(totalAmount) + "</em></p>\n";
		result += "<p>You earned <em>" + String.valueOf(frequentRenterPoints) + "</em> frequent renter points</p>";
        return result;
    }
   
}
