FLX PDA Trader Restock 1.0

Adds the paid Restock button to the PDA Contacts tab, above the contact list.
The Contacts tab has its own confirmation/result dialog.
Does not alter the Taskboard controls or category list.
One confirmed order costs 25,000 RU for all initialized trader supply profiles.
Ordinary stalkers and companions without supply assortments are excluded.
Current-level traders restock through trade_manager.update(npc, true), retaining
the existing supply conditions, goodwill requirements and autoinjector addons.
Distant/offline traders retain an expired supply timer in their normal saved
trade profiles and restock on their next normal update. No extra save format.
New traders not yet initialized use their normal initial supply generation.
Orders cannot expand the trader's unlocked supply tier.
Insufficient money, missing profiles and canceling never charge the player.
Disabling this addon removes its button; already ordered deliveries remain due.

Validation: Lua scenario tests with engine API stubs; in-game check still needed.
