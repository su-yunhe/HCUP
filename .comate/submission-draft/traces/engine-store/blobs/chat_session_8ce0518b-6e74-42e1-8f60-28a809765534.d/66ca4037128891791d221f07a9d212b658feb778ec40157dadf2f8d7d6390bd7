/**
 * 仅当栈顶仍是 current 页面时才跳转，避免快速连点重复入栈
 */
export function pushPathFrom(stack: NavPathStack, current: string, name: string, param: Object | null): void {
  const names = stack.getAllPathName();
  if (names.length > 0 && names[names.length - 1] !== current) {
    return;
  }
  stack.pushPathByName(name, param);
}
