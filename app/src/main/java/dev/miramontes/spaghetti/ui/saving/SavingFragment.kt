package dev.miramontes.spaghetti.ui.saving

import android.content.Intent
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.ListView
import androidx.fragment.app.Fragment
import dev.miramontes.spaghetti.NewAccountActivity
import dev.miramontes.spaghetti.R

class SavingFragment : Fragment() {
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        val root = inflater.inflate(R.layout.fragment_saving, container, false)

        // Populate account information
        val savingsList: ListView = root.findViewById(R.id.savings_list)
        val adapter =
            SavingsListAdapter(this.requireContext())
        savingsList.adapter = adapter

        val newAccountButton = root.findViewById<Button>(R.id.new_account_button)
        newAccountButton.setOnClickListener{
            val intent = Intent(activity, NewAccountActivity::class.java).apply {
                putExtra("spaghetti.account_type", "savings")
            }
            startActivity(intent)
        }

        return root
    }
}