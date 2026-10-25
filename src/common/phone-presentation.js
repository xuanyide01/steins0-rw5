// Mode 13 is Amadeus. W6613 may still name the last ordinary RINE contact.
// Normalize old saved pending choices at display time as well as new graph data.
export function callContact(choice){return choice&&choice.mode===13?3:choice&&choice.contact;}
export function callHeading(choice){if(!choice)return '来电';if(choice.kind==='call'&&choice.mode===13)return 'Amadeus 来电';return choice.heading||'来电';}
