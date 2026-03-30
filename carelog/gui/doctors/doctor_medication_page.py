import streamlit as st
from helper_manager.medication_manager import (
	edit_medications,
	remove_medication,
	list_medications
)
from helper_manager.record_manager import (
	add_record_doctor
)

# starting of the medication page
def medication_page(manager, username):
	st.header("Medications")

	tab1, tab2, tab3, tab4 = st.tabs([
		"Assign",
		"Edit Record",
		"Remove From Record",
		"List",
	])
	# assgin medications to patient 
	with tab1:
		st.subheader("Assign Medications")
		with st.form("assign_meds_form"):
			pid = st.text_input("Patient ID", key="assign_pid").strip()
			meds_input = st.text_area(
				"Medications (comma-separated or one per line)",
				height=100,
			)
			make_new = st.checkbox("Create a new record for this prescription", value=False)
			
			instructions = st.text_input("Instructions (optional)")
			submit_assign = st.form_submit_button("Assign")

			if submit_assign:
				meds_str = meds_input.replace("\n", ",")
				if not pid:
					st.error("Please provide a patient ID")
				elif not meds_str.strip():
					st.error("Please enter at least one medication")
				else:
					ok, msg, rec_id = add_record_doctor(
						patient_id=pid,
						medications=meds_str,
						doctor_username=username,
						instructions=instructions,
						new_record=make_new,
					)
					if ok:
						st.success(f"{msg}. Record ID: {rec_id}")
					else:
						st.error(msg)
	
	# edit medications on existing record
	with tab2:
		st.subheader("Edit Record Medications")
		with st.form("edit_meds_form"):
			rid = st.text_input("Record ID (e.g., PR0007)", key="edit_rid").strip()
			meds_input = st.text_area(
				"New medications (comma-separated or one per line)",
				height=100,
			)
			submit_edit = st.form_submit_button("Replace Medications")

			if submit_edit:
				meds_str = meds_input.replace("\n", ",")
				if not rid:
					st.error("Please provide a record ID")
				else:
					ok, msg = edit_medications(rid, meds_str)
					if ok:
						st.success(msg)
					else:
						st.error(msg)
	
	# remove one medication from record
	with tab3:
		st.subheader("Remove One Medication From Record")
		with st.form("remove_med_form"):
			rid = st.text_input("Record ID (e.g., PR0007)", key="remove_rid").strip()
			med = st.text_input("Medication to remove (exact text)", key="remove_med").strip()
			submit_remove = st.form_submit_button("Remove")

			if submit_remove:
				if not rid or not med:
					st.error("Please provide record ID and medication text")
				else:
					ok, msg = remove_medication(rid, med)
					if ok:
						st.success(msg)
					else:
						st.error(msg)
	
	# list medications for a patient 
	with tab4:
		st.subheader("List Medications")
		pid = st.text_input("Patient ID", key="list_pid").strip()
		per_record = st.checkbox("Group by record", value=False)
		if st.button("List", key="list_btn"):
			if not pid:
				st.error("Please provide a patient ID")
			else:
				ok, msg, data = list_medications(pid, per_record=per_record)
				if ok:
					st.success(msg)
					if per_record:
						for row in data:
							with st.expander(f"{row.get('record_id','')} — {row.get('timestamp','')}"):
								meds = row.get("medications", [])
								if meds:
									for m in meds:
										st.write(f"• {m}")
								else:
									st.caption("No medications on this record")
					else:
						if data:
							for m in data:
								st.write(f"• {m}")
						else:
							st.caption("No medications found for this patient")
				else:
					st.error(msg)
