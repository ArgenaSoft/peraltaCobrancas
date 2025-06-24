import { format } from 'date-fns';

function readable_date(input: Date | string): string {
    const date = typeof input === 'string'
        ? parseLocalDate(input)
        : input;

    if (isNaN(date.getTime())) {
        throw new Error('Invalid date');
    }

    return format(date, 'dd/MM/yyyy');
}

function parseLocalDate(dateStr: string): Date {
    const [year, month, day] = dateStr.split('-').map(Number);
    return new Date(year, month - 1, day);
}

export { readable_date, parseLocalDate };