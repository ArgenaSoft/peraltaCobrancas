interface TextProps {
    placeholder: string;
    value: string;
    callback: (value: string) => void;
    classes?: string;
    onKeyDown?: (e: React.KeyboardEvent<HTMLInputElement>) => void;
    autoComplete?: string;
}

const TextInput = (props: TextProps) => {
    function handleChange(e: any) {
        props.callback(e.target.value);
    }

    return (
        <input
        type="text"
        className={`border-black border-2 rounded-lg text-black p-2 ${props.classes}`}
        value={props.value}
        onChange={handleChange}
        placeholder={props.placeholder}
        onKeyDown={props.onKeyDown}
        autoComplete={props.autoComplete}
        />
    );
}

export default TextInput;