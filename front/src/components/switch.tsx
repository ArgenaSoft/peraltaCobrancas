interface SwitchProps  {
    state: boolean;
    onValue: string;
    offValue: string;
    setState: (value: boolean) => void;
}

export default function Switch(props: SwitchProps) {
    return(
        <span 
            className={`box-border text-center border-2 ${props.state ? 'text-dark-blue bg-white border-dark-blue' : 'text-white bg-dark-blue'} 
            rounded-full p-2 text-[12px] font-bold ml-[1px]`}
            onClick={() => props.setState(!props.state)}
        >
            {props.state ? props.onValue : props.offValue}
        </span>
    )
}