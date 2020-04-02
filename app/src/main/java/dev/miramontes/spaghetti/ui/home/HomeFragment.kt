package dev.miramontes.spaghetti.ui.home

import android.content.Context
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.fragment.app.Fragment
import dev.miramontes.spaghetti.R
import dev.miramontes.spaghetti.library.generateDebugSpaghettiAmount
import dev.miramontes.spaghetti.library.getIdToken

class HomeFragment : Fragment() {
    private var idToken: String? = null
    private lateinit var amountTextView: TextView

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        val root = inflater.inflate(R.layout.fragment_home, container, false)
        amountTextView = root.findViewById(R.id.amount)
        return root
    }

    override fun onAttach(context: Context) {
        super.onAttach(context)

        idToken = getIdToken(context)
        if (idToken == null) {
            activity?.finish()
        }

        val amount = generateDebugSpaghettiAmount()
        amountTextView.text = String.format("%.2f", amount)
    }
}