import { format } from "date-fns/format";


function readable_date(date: Date | string): string {
    if (typeof date === 'string') {
        date = new Date(date);
    }
    
    return format(date, 'dd/MM/yyyy');
}

export { readable_date };