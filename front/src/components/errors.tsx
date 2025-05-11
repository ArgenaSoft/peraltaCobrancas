export class FriendlyError extends Error {
  public status?: number;
  public original?: unknown;

  constructor(message: string, status?: number, original?: unknown) {
    super(message);
    this.name = "FriendlyError";
    this.status = status;
    this.original = original;
  }
}
