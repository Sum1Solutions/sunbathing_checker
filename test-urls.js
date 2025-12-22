// Test the FIXED URL patterns
const locations = ['Fort Lauderdale', 'Miami', 'Naples'];
const checkin = '2025-01-01';
const checkout = '2025-01-15';
const maxBudget = 199;

const locationMap = {
    'Naples': { airbnb: 'Naples--FL', vrbo: 'Naples,+Florida' },
    'Fort Lauderdale': { airbnb: 'Fort-Lauderdale--FL', vrbo: 'Fort+Lauderdale,+Florida' },
    'Miami': { airbnb: 'Miami--FL', vrbo: 'Miami,+Florida' }
};

// FIXED: Parse as local date to avoid timezone issues
function formatMarriottDate(dateStr) {
    const [year, month, day] = dateStr.split('-').map(Number);
    return `${month.toString().padStart(2, '0')}/${day.toString().padStart(2, '0')}/${year}`;
}

console.log('URL TEST RESULTS (FIXED)\n========================\n');

locations.forEach(locationName => {
    const loc = locationMap[locationName];
    console.log(`=== ${locationName} ===\n`);

    // Airbnb - working
    const airbnbUrl = `https://www.airbnb.com/s/${loc.airbnb}/homes?checkin=${checkin}&checkout=${checkout}&price_max=${maxBudget}`;
    console.log('Airbnb:\n  ' + airbnbUrl + '\n');

    // VRBO - working
    const vrboUrl = `https://www.vrbo.com/search?destination=${loc.vrbo}&startDate=${checkin}&endDate=${checkout}&adults=2`;
    console.log('VRBO:\n  ' + vrboUrl + '\n');

    // Booking.com - FIXED: full location format
    const bookingUrl = `https://www.booking.com/searchresults.html?ss=${encodeURIComponent(locationName + ', Florida, United States')}&checkin=${checkin}&checkout=${checkout}`;
    console.log('Booking:\n  ' + bookingUrl + '\n');

    // Hotels.com - NEW
    const hotelsComUrl = `https://www.hotels.com/Hotel-Search?destination=${encodeURIComponent(locationName + ', FL')}&startDate=${checkin}&endDate=${checkout}&adults=2`;
    console.log('Hotels.com:\n  ' + hotelsComUrl + '\n');

    // Google Hotels - working
    const googleUrl = `https://www.google.com/travel/hotels/${encodeURIComponent(locationName + ' Florida')}?q=${encodeURIComponent(locationName + ' hotels')}&dates=${checkin.replace(/-/g, '')}%2C${checkout.replace(/-/g, '')}`;
    console.log('Google:\n  ' + googleUrl + '\n');

    // Marriott - FIXED: different endpoint + correct date format
    const marriottUrl = `https://www.marriott.com/search/findHotels.mi?searchType=InCity&destinationAddress.city=${encodeURIComponent(locationName)}&destinationAddress.stateProvince=FL&destinationAddress.country=US&fromDate=${formatMarriottDate(checkin)}&toDate=${formatMarriottDate(checkout)}&flexibleDateSearch=false`;
    console.log('Marriott:\n  ' + marriottUrl + '\n');

    // Luxury Beach - FIXED
    const luxuryBeachUrl = `https://www.booking.com/searchresults.html?ss=${encodeURIComponent(locationName + ', Florida, United States')}&checkin=${checkin}&checkout=${checkout}&class=5&nflt=class%3D5`;
    console.log('Luxury Beach:\n  ' + luxuryBeachUrl + '\n');
});
