import { useEffect, useRef, useState } from "react";
import type { CashAccount } from "../types";

interface Props {
  account: CashAccount | null;
}

export function CashBalanceBadge({ account }: Props) {
  const [flashClass, setFlashClass] = useState("");
  const prevBalanceRef = useRef<number | null>(null);

  useEffect(() => {
    if (!account) return;
    const prev = prevBalanceRef.current;
    if (prev !== null && account.balance !== prev) {
      setFlashClass(account.balance < prev ? "flash-drop" : "flash-up");
      const t = setTimeout(() => setFlashClass(""), 900);
      prevBalanceRef.current = account.balance;
      return () => clearTimeout(t);
    }
    prevBalanceRef.current = account.balance;
  }, [account]);

  if (!account) {
    return <div className="cash-badge loading">Loading balance…</div>;
  }

  return (
    <div className={`cash-badge ${flashClass}`}>
      <div className="cash-label">Checking</div>
      <div className="cash-amount">
        $
        {account.balance.toLocaleString(undefined, {
          minimumFractionDigits: 2,
          maximumFractionDigits: 2,
        })}
      </div>
      <div className="cash-date">as of {account.date}</div>
    </div>
  );
}
