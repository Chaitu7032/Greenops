export interface NavLinkItem {
  name: string;
  href: string;
}

export const NAVIGATION_LINKS: NavLinkItem[] = [
  { name: "Dashboard", href: "/dashboard" },
  { name: "Pipelines", href: "/pipelines" },
  { name: "Repositories", href: "/repositories" },
  { name: "Sprints", href: "/sprints" },
  { name: "Policies", href: "/policies" },
  { name: "Settings", href: "/settings" },
];
