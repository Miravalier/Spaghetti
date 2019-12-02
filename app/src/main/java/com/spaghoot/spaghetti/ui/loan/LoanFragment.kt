package com.spaghoot.spaghetti.ui.loan

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.fragment.app.Fragment
import androidx.lifecycle.Observer
import androidx.lifecycle.ViewModelProviders
import com.spaghoot.spaghetti.R

class LoanFragment : Fragment() {

    private lateinit var loanViewModel: LoanViewModel

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        loanViewModel =
            ViewModelProviders.of(this).get(LoanViewModel::class.java)
        val root = inflater.inflate(R.layout.fragment_loan, container, false)

        return root
    }
}