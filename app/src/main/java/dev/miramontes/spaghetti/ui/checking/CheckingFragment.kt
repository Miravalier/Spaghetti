package dev.miramontes.spaghetti.ui.checking

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
import org.json.JSONObject
import java.net.URL

class CheckingFragment : Fragment() {
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        val root = inflater.inflate(R.layout.fragment_checking, container, false)

        // Populate account information
        val savingsList: ListView = root.findViewById(R.id.checking_list)
        val adapter =
            CheckingListAdapter(this.requireContext())
        savingsList.adapter = adapter

        val newAccountButton = root.findViewById<Button>(R.id.new_account_button)
        newAccountButton.setOnClickListener{
            val intent = Intent(activity, NewAccountActivity::class.java).apply {
                putExtra("spaghetti.account_type", "checking")
            }
            startActivity(intent)
        }

        val response: String = URL("https://miravalier.net/login").openConnection().content as String? ?: "{}"
        val json = JSONObject(response)
        val abc: String? = json.getString("abc")

        return root
    }
}