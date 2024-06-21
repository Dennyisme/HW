package movierental;

public abstract class  Movie {
    public static final int CHILDRENS = 2;
    public static final int NEW_RELEASE = 1;
    public static final int REGULAR = 0;
	
	
    protected String _title;
    protected int _priceCode;
	protected double amount = 0;
	protected int frequentRentalPoint = 0;


    public Movie(String title, int priceCode) {
        _title = title;
        _priceCode = priceCode;
    }

//    public int getPriceCode() {
//        return _priceCode;
//    }
//
//    public void setPriceCode(int arg) {
//        _priceCode = arg;
//    }
//    
    public String getTitle() {
        return _title;
    }
    
    public abstract double getamount(Rental getamount);
    
    public abstract int getfrequentRentalPoint(Rental rental);
 
}
