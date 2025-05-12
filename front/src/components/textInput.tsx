import { InputMask } from '@react-input/mask';

interface TextProps {
    placeholder: string;
    value: string;
    callback: (value: string) => void;
    classes?: string;
    onKeyDown?: (e: React.KeyboardEvent<HTMLInputElement>) => void;
    autoComplete?: string;
    mask?: string;
    replacement?: Record<string, RegExp>;
}

const TextInput = (props: TextProps) => {
    function handleChange(e: any) {
        console.log(e.target.value);
        props.callback(e.target.value);
    }

    if(props.mask && props.replacement) {
        return <InputMask 
            mask={props.mask}
            replacement={props.replacement}
            className={`border-black border-2 rounded-lg text-black p-2 ${props.classes}`}
            onChange={handleChange} 
            value={props.value}
            placeholder={props.placeholder}
            onKeyDown={props.onKeyDown}
            autoComplete={props.autoComplete}
        />
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