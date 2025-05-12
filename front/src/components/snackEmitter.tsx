
const emitter = new EventTarget();

export function emitSnack(title: string, msg: string, level: string) {
    emitter.dispatchEvent(new CustomEvent("snack", { detail: { title, msg, level } }));
}

export function onSnack(callback: (title: string, msg: string, level: string) => void) {
    const handler = (e: Event) => {
      const custom = e as CustomEvent<{ title: string, msg: string, level: string }>
      callback(custom.detail.title, custom.detail.msg, custom.detail.level);
    }
    emitter.addEventListener('snack', handler)
    return () => emitter.removeEventListener('snack', handler)
  }