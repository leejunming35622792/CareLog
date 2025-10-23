import streamlit as st
from datetime import datetime, timedelta
import pandas as pd

def shift_page(manager):
    manager = st.session_state.manager
    username = st.session_state.username
    doctor = next((d for d in manager.doctors if d.username == username), None)

    st.subheader("Shift Schedule")
    if not doctor:
        st.warning("No doctor found for this username.")
        return

    all_shifts = [s.__dict__ for s in manager.shifts if s.staff_id == doctor.d_id]
    if not all_shifts:
        st.info("No shifts assigned yet.")
        return

    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    times = [f"{h:02d}:00" for h in range(8, 21)]
    schedule_df = pd.DataFrame(index=times, columns=days)
    schedule_df[:] = ""

    for shift in all_shifts:
        day = shift["day"]
        start = datetime.strptime(shift["start_time"], "%H:%M")
        end = datetime.strptime(shift["end_time"], "%H:%M")
        remark = shift["remark"]

        current = start
        while current < end:
            time_str = current.strftime("%H:00")
            if day in schedule_df.columns and time_str in schedule_df.index:
                schedule_df.loc[time_str, day] = remark
            current += timedelta(hours=1)

    st.dataframe(
        schedule_df.style.set_properties(
            subset=pd.IndexSlice[:, :],
            **{"text-align": "center", "white-space": "pre-wrap"}
        ),
        use_container_width=True,
        height=500
    )